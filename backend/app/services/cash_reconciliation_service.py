"""\
Cash reconciliation service

Goal:
- Estimate untracked cash in wallet using ATM withdrawals minus tracked cash expenses.
- Generate probabilistic, pattern-based expense suggestions for quick entry.

This uses lightweight heuristics and historical user data (no external ML dependency).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.transaction import Transaction, TransactionType


_CASH_WITHDRAW_KEYWORDS = ("atm", "cash withdrawal", "withdrawal", "withdraw", "cash withdraw")


def _normalize_text(value: Optional[str]) -> str:
    return (value or "").strip().lower()


def _has_tag(txn: Transaction, tag: str) -> bool:
    try:
        return tag in (txn.tags or [])
    except Exception:
        return False


def _is_cash_withdrawal(txn: Transaction) -> bool:
    if txn.transaction_type != TransactionType.DEBIT:
        return False

    # Primary signal: explicit tag
    if _has_tag(txn, "cash_withdrawal"):
        return True

    # Heuristic fallback
    text = " ".join([
        _normalize_text(txn.description),
        _normalize_text(txn.merchant_name),
        _normalize_text(txn.merchant_category),
    ])
    return any(k in text for k in _CASH_WITHDRAW_KEYWORDS)


def _is_cash_spend(txn: Transaction) -> bool:
    if txn.transaction_type != TransactionType.DEBIT:
        return False

    # Primary signal: explicit tag(s)
    if _has_tag(txn, "cash") or _has_tag(txn, "cash_spend"):
        return True

    # Secondary: manual entries whose description indicates cash
    text = " ".join([
        _normalize_text(txn.description),
        _normalize_text(txn.subcategory),
    ])
    return "cash" in text


@dataclass(frozen=True)
class CashCheckSuggestion:
    label: str
    subcategory: str
    typical_amount: int
    amount_range: Tuple[int, int]
    probability: float


class CashReconciliationService:
    """Compute cash position and build quick-entry suggestions."""

    async def compute_cash_position(
        self,
        db: AsyncSession,
        user_id: str,
        lookback_days: int = 30,
        min_days_since_withdrawal: int = 3,
    ) -> Dict[str, Any]:
        """\
        Compute user's untracked cash based on withdrawals minus tracked cash expenses.

        Returns a JSON-friendly dict.
        """

        now = datetime.utcnow()
        start_date = now - timedelta(days=lookback_days)

        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.transaction_date >= start_date)
            .order_by(Transaction.transaction_date.desc())
        )
        txns = result.scalars().all()

        withdrawals: List[Transaction] = [t for t in txns if _is_cash_withdrawal(t)]
        cash_spends: List[Transaction] = [t for t in txns if _is_cash_spend(t)]

        last_withdrawal_date: Optional[datetime] = withdrawals[0].transaction_date if withdrawals else None
        days_since_withdrawal: Optional[int] = None
        if last_withdrawal_date:
            days_since_withdrawal = max(0, (now - last_withdrawal_date).days)

        total_withdrawn = float(sum(t.amount for t in withdrawals))
        total_tracked_cash_spend = float(sum(t.amount for t in cash_spends))
        estimated_untracked_cash = max(0.0, total_withdrawn - total_tracked_cash_spend)

        return {
            "user_id": user_id,
            "lookback_days": lookback_days,
            "last_withdrawal_date": last_withdrawal_date.isoformat() if last_withdrawal_date else None,
            "days_since_withdrawal": days_since_withdrawal,
            "total_withdrawn": total_withdrawn,
            "tracked_cash_spend": total_tracked_cash_spend,
            "estimated_untracked_cash": float(estimated_untracked_cash),
            "eligible_for_nudge": bool(
                estimated_untracked_cash > 0
                and days_since_withdrawal is not None
                and days_since_withdrawal >= min_days_since_withdrawal
            ),
        }

    async def suggest_likely_cash_expenses(
        self,
        db: AsyncSession,
        user_id: str,
        target_date: Optional[datetime] = None,
        history_days: int = 90,
        limit: int = 4,
    ) -> List[CashCheckSuggestion]:
        """\
        Produce probabilistic quick-add cash expense suggestions.

        Approach:
        - Use historical cash spends (tagged "cash"/"cash_spend" or description includes "cash").
        - Weight by same weekday as target_date.
        - Suggest common subcategories with robust typical amount.
        """

        now = datetime.utcnow()
        target_date = target_date or now
        start_date = target_date - timedelta(days=history_days)
        target_weekday = target_date.weekday()  # Monday=0

        result = await db.execute(
            select(Transaction)
            .where(Transaction.user_id == user_id)
            .where(Transaction.transaction_type == TransactionType.DEBIT)
            .where(Transaction.transaction_date >= start_date)
            .order_by(Transaction.transaction_date.desc())
        )
        txns = [t for t in result.scalars().all() if _is_cash_spend(t)]

        if not txns:
            # Sensible defaults when there is no history.
            defaults = [
                ("Groceries", "groceries", 500, (300, 700), 0.34),
                ("Food", "food", 200, (120, 350), 0.28),
                ("Transport", "transport", 100, (50, 200), 0.22),
                ("Misc", "misc", 150, (80, 300), 0.16),
            ]
            return [
                CashCheckSuggestion(label=a, subcategory=b, typical_amount=c, amount_range=d, probability=e)
                for a, b, c, d, e in defaults[:limit]
            ]

        # Aggregate amounts per subcategory (fallback to merchant_category / other)
        bucket_amounts: Dict[str, List[float]] = {}
        bucket_weight: Dict[str, float] = {}

        for t in txns:
            subcat = (t.subcategory or "").strip().lower() or (t.merchant_category or "").strip().lower() or "other"
            # Weight same weekday higher to reflect routine.
            w = 1.0
            if t.transaction_date.weekday() == target_weekday:
                w = 1.6
            bucket_amounts.setdefault(subcat, []).append(float(t.amount))
            bucket_weight[subcat] = bucket_weight.get(subcat, 0.0) + w

        # Compute probability mass and robust amount ranges.
        total_weight = sum(bucket_weight.values()) or 1.0
        ranked = sorted(bucket_weight.items(), key=lambda kv: kv[1], reverse=True)

        suggestions: List[CashCheckSuggestion] = []
        for subcat, w in ranked[: max(limit, 10)]:
            amounts = sorted(bucket_amounts.get(subcat, []))
            if not amounts:
                continue

            def _percentile(p: float) -> float:
                if len(amounts) == 1:
                    return amounts[0]
                idx = int(round((len(amounts) - 1) * p))
                return amounts[max(0, min(idx, len(amounts) - 1))]

            p25 = _percentile(0.25)
            p50 = _percentile(0.50)
            p75 = _percentile(0.75)

            typical = int(round(p50))
            low = int(max(0, round(p25)))
            high = int(max(low, round(p75)))
            prob = float(w / total_weight)

            label = subcat.replace("_", " ").title()
            suggestions.append(
                CashCheckSuggestion(
                    label=label,
                    subcategory=subcat,
                    typical_amount=typical,
                    amount_range=(low, high),
                    probability=prob,
                )
            )

        # Normalize + take top N
        suggestions = suggestions[:limit]
        prob_sum = sum(s.probability for s in suggestions) or 1.0
        return [
            CashCheckSuggestion(
                label=s.label,
                subcategory=s.subcategory,
                typical_amount=s.typical_amount,
                amount_range=s.amount_range,
                probability=float(s.probability / prob_sum),
            )
            for s in suggestions
        ]


cash_reconciliation_service = CashReconciliationService()
