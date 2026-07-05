"""Credit card recommendation endpoints.

These endpoints invoke the CreditCardAgent (which has web-search tools) and
return structured card recommendations for the frontend.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.logging import get_logger
from app.dependencies import CurrentUser


logger = get_logger(__name__)

router = APIRouter(prefix="/credit-cards", tags=["Credit Cards"])


class CreditCardRecommendationRequest(BaseModel):
    spending_category: str = Field(default="general")
    monthly_spending: int = Field(default=50000, ge=0)
    annual_income: int = Field(default=1000000, ge=0)
    country: str = Field(default="India")
    max_results: int = Field(default=8, ge=1, le=12)


class CreditCardRecommendation(BaseModel):
    id: str
    name: str
    issuer: Optional[str] = None
    annual_fee: Optional[str] = None
    joining_fee: Optional[str] = None
    best_for: List[str] = Field(default_factory=list)
    rewards_summary: Optional[str] = None
    key_benefits: List[str] = Field(default_factory=list)
    eligibility: Optional[str] = None
    apply_url: Optional[str] = None
    sources: List[str] = Field(default_factory=list)


class CreditCardRecommendationResponse(BaseModel):
    cards: List[CreditCardRecommendation]
    generated_at: str
    raw_output: Optional[str] = None


def _try_parse_json_blob(text: str) -> Optional[Any]:
    """Best-effort extraction of a JSON object/array from free-form LLM output."""

    if not text:
        return None

    # Fast path: whole string is JSON.
    try:
        return json.loads(text)
    except Exception:
        pass

    # Try fenced code block first.
    m = re.search(r"```(?:json)?\s*(\{.*?\}|\[.*?\])\s*```", text, flags=re.DOTALL | re.IGNORECASE)
    if m:
        try:
            return json.loads(m.group(1))
        except Exception:
            pass

    # Try to extract the largest object or array-like span.
    obj_start = text.find("{")
    obj_end = text.rfind("}")
    if 0 <= obj_start < obj_end:
        candidate = text[obj_start : obj_end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    arr_start = text.find("[")
    arr_end = text.rfind("]")
    if 0 <= arr_start < arr_end:
        candidate = text[arr_start : arr_end + 1]
        try:
            return json.loads(candidate)
        except Exception:
            pass

    return None


def _normalize_cards(payload: Any) -> List[Dict[str, Any]]:
    """Convert various plausible JSON shapes into a list of card dicts."""

    if payload is None:
        return []

    if isinstance(payload, dict):
        # Common shapes: {"cards": [...]}, {"recommendations": [...]}, {"results": [...]}
        for key in ("cards", "recommendations", "results", "data"):
            val = payload.get(key)
            if isinstance(val, list):
                return [x for x in val if isinstance(x, dict)]
        # Or a single card dict
        if "name" in payload:
            return [payload]

    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]

    return []


def _fallback_cards(spending_category: str) -> List[CreditCardRecommendation]:
    # Conservative fallback (keeps UX working even if agent/web search fails).
    # Note: values are illustrative; live accuracy depends on web sources.
    base = [
        {
            "id": "hdfc-millennia",
            "name": "HDFC Millennia",
            "issuer": "HDFC Bank",
            "best_for": ["shopping", "online", "general"],
            "rewards_summary": "Cashback-focused card for common online merchants.",
            "key_benefits": [
                "Cashback on select online spends",
                "Fuel surcharge waiver (terms apply)",
                "Milestone/merchant offers (varies)",
            ],
        },
        {
            "id": "icici-amazon-pay",
            "name": "Amazon Pay ICICI",
            "issuer": "ICICI Bank",
            "best_for": ["shopping", "online"],
            "rewards_summary": "Strong value for Amazon users; simple cashback structure.",
            "key_benefits": [
                "Cashback on Amazon purchases (varies by membership)",
                "No/low annual fee (variant-dependent)",
            ],
        },
        {
            "id": "sbi-simplyclick",
            "name": "SBI SimplyCLICK",
            "issuer": "SBI Card",
            "best_for": ["online", "shopping"],
            "rewards_summary": "Rewards-focused online card with partner accelerated points.",
            "key_benefits": [
                "Accelerated rewards on partner brands",
                "Welcome benefits (offer-dependent)",
            ],
        },
        {
            "id": "hdfc-regalia",
            "name": "HDFC Regalia",
            "issuer": "HDFC Bank",
            "best_for": ["travel", "premium"],
            "rewards_summary": "Travel-friendly rewards card with lounge/benefits on some variants.",
            "key_benefits": [
                "Reward points on spends",
                "Travel and lounge benefits (variant-dependent)",
            ],
        },
    ]

    if spending_category and spending_category != "general":
        preferred = [c for c in base if spending_category in c.get("best_for", [])]
        if preferred:
            base = preferred + [c for c in base if c not in preferred]

    return [CreditCardRecommendation(**c) for c in base]


@router.post("/recommendations", response_model=CreditCardRecommendationResponse)
async def get_credit_card_recommendations(
    request: CreditCardRecommendationRequest,
    current_user: CurrentUser,
):
    """Recommend credit cards using the CreditCardAgent + web-search tools."""

    spending_category = (request.spending_category or "general").strip()

    user_input = (
        "You are helping a user pick the best credit cards. "
        "Use web search tools to find recent sources and include 1-3 source URLs per card. "
        "Return ONLY valid JSON (no markdown) in this exact shape:\n\n"
        "{\n"
        "  \"cards\": [\n"
        "    {\n"
        "      \"id\": \"string_slug\",\n"
        "      \"name\": \"Card Name\",\n"
        "      \"issuer\": \"Bank/Issuer\",\n"
        "      \"annual_fee\": \"string_or_null\",\n"
        "      \"joining_fee\": \"string_or_null\",\n"
        "      \"best_for\": [\"category\"],\n"
        "      \"rewards_summary\": \"short summary\",\n"
        "      \"key_benefits\": [\"benefit 1\", \"benefit 2\"],\n"
        "      \"eligibility\": \"short eligibility guidance\",\n"
        "      \"apply_url\": \"url_or_null\",\n"
        "      \"sources\": [\"url1\", \"url2\"]\n"
        "    }\n"
        "  ]\n"
        "}\n\n"
        f"User profile:\n"
        f"- Country: {request.country}\n"
        f"- Primary spending category: {spending_category}\n"
        f"- Monthly spending: INR {request.monthly_spending}\n"
        f"- Annual income: INR {request.annual_income}\n"
        f"Recommend up to {request.max_results} cards relevant to the category and income band. "
        "Avoid hallucinating exact fees if unsure; you can write 'Check latest on issuer site'."
    )

    try:
        from agents.block_3.credit_card_agent import CreditCardAgent

        agent = CreditCardAgent()
        result = await agent.run(user_input, context={"user_id": current_user.id})
        output_text = (result or {}).get("output", "")

        parsed = _try_parse_json_blob(output_text)
        cards_raw = _normalize_cards(parsed)

        cards: List[CreditCardRecommendation] = []
        for idx, card in enumerate(cards_raw[: request.max_results]):
            # Ensure a stable id exists
            card_id = card.get("id")
            if not card_id:
                name = str(card.get("name") or f"card-{idx}")
                card_id = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-") or f"card-{idx}"
                card["id"] = card_id
            cards.append(CreditCardRecommendation(**card))

        if not cards:
            cards = _fallback_cards(spending_category)

        return CreditCardRecommendationResponse(
            cards=cards[: request.max_results],
            generated_at=datetime.utcnow().isoformat(),
            raw_output=output_text,
        )

    except Exception as e:
        logger.error("credit_card_recommendations_failed", error=str(e))
        cards = _fallback_cards(spending_category)
        return CreditCardRecommendationResponse(
            cards=cards[: request.max_results],
            generated_at=datetime.utcnow().isoformat(),
            raw_output=None,
        )
