"""agents.tools.web_search_tool

Lightweight "web search" tools used by agents.

Important: This module intentionally does NOT depend on Finnhub/NewsAPI keys.
It fetches headlines via public RSS feeds (Google News) and returns a small,
structured list (title/source/url/published_at).
"""

from __future__ import annotations

from typing import List, Optional
from langchain_core.tools import tool
import httpx
from datetime import datetime
from email.utils import parsedate_to_datetime
import html
import re
import xml.etree.ElementTree as ET


def _google_news_rss_url(query: str, *, hl: str = "en-IN", gl: str = "IN", ceid: str = "IN:en") -> str:
    # Google News RSS Search endpoint.
    # Example: https://news.google.com/rss/search?q=indian%20stock%20market&hl=en-IN&gl=IN&ceid=IN:en
    q = httpx.QueryParams({"q": query}).get("q")
    return f"https://news.google.com/rss/search?q={q}&hl={hl}&gl={gl}&ceid={ceid}"


def _strip_html(text: str) -> str:
    if not text:
        return ""
    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _guess_sentiment_from_title(title: str) -> str:
    headline = (title or "").lower()
    if any(word in headline for word in ["surge", "rally", "gain", "up", "high", "positive", "growth", "record", "beats"]):
        return "positive"
    if any(word in headline for word in ["fall", "drop", "down", "low", "negative", "loss", "decline", "miss", "slump"]):
        return "negative"
    return "neutral"


async def _fetch_rss_items(query: str, max_results: int) -> List[dict]:
    url = _google_news_rss_url(query)
    async with httpx.AsyncClient(follow_redirects=True) as client:
        resp = await client.get(url, timeout=12.0)
        resp.raise_for_status()

    root = ET.fromstring(resp.text)
    channel = root.find("channel")
    if channel is None:
        return []

    items: List[dict] = []
    for item in channel.findall("item"):
        if len(items) >= max_results:
            break

        raw_title = (item.findtext("title") or "").strip()
        link = (item.findtext("link") or "").strip()
        raw_desc = (item.findtext("description") or "").strip()
        pub_date = (item.findtext("pubDate") or "").strip()
        source_el = item.find("source")

        source: Optional[str] = None
        if source_el is not None and (source_el.text or "").strip():
            source = (source_el.text or "").strip()
        elif " - " in raw_title:
            # Google News often formats as: "Headline - Publisher"
            source = raw_title.rsplit(" - ", 1)[-1].strip()

        published_at = ""
        if pub_date:
            try:
                published_at = parsedate_to_datetime(pub_date).astimezone().isoformat()
            except Exception:
                published_at = pub_date

        items.append(
            {
                "title": raw_title,
                "summary": _strip_html(raw_desc)[:300],
                "source": source or "Google News",
                "url": link,
                "published_at": published_at,
                "sentiment": _guess_sentiment_from_title(raw_title),
            }
        )

    return items


@tool
async def search_financial_news(query: str, max_results: int = 5) -> dict:
    """
    Search for financial news via web search (RSS).
    
    Args:
        query: Search query (e.g., "Indian stock market", "Nifty 50")
        max_results: Maximum number of results
        
    Returns:
        Dict containing a list of articles with title/source/url/published_at
    """
    try:
        results = await _fetch_rss_items(query=query, max_results=max_results)
        return {
            "query": query,
            "provider": "google_news_rss",
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        return {
            "query": query,
            "provider": "google_news_rss",
            "results": [],
            "count": 0,
            "error": str(e),
        }
    
    return {
        "query": query,
        "results": results,
        "count": len(results)
    }


@tool
async def search_stock_news(symbol: str = "AAPL", max_results: int = 5) -> dict:
    """
    Get company-specific stock news via web search (RSS).
    
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'RELIANCE.NS')
        max_results: Maximum number of results
        
    Returns:
        Company-specific news articles
    """
    query = f"{symbol} stock news"
    try:
        results = await _fetch_rss_items(query=query, max_results=max_results)
        return {
            "symbol": symbol,
            "query": query,
            "provider": "google_news_rss",
            "results": results,
            "count": len(results),
        }
    except Exception as e:
        return {
            "symbol": symbol,
            "query": query,
            "provider": "google_news_rss",
            "results": [],
            "count": 0,
            "error": str(e),
        }


@tool
def search_market_trends(sector: str = "general") -> dict:
    """
    Get current market trends.
    
    Args:
        sector: Market sector to focus on
        
    Returns:
        Current market trends and analysis
    """
    return {
        "sector": sector,
        "trends": [
            {
                "trend": "Market showing positive momentum",
                "description": "Indian markets demonstrate resilience with banking and IT leading gains",
                "sentiment": "positive"
            }
        ],
        "note": "Use search_financial_news for real-time market updates"
    }


@tool
def search_credit_cards(spending_category: str) -> dict:
    """
    Search for credit cards by spending category.
    
    Args:
        spending_category: Primary spending category
        
    Returns:
        Recommended credit cards
    """
    # Placeholder with common Indian credit cards
    cards = {
        "shopping": [
            {"name": "HDFC Millennia", "rewards": "5% cashback on online shopping"},
            {"name": "Amazon Pay ICICI", "rewards": "5% on Amazon, 2% on others"}
        ],
        "travel": [
            {"name": "HDFC Infinia", "rewards": "5 reward points per ₹150"},
            {"name": "Axis Atlas", "rewards": "Premium travel benefits"}
        ],
        "fuel": [
            {"name": "BPCL SBI Card", "rewards": "13X rewards on BPCL"},
            {"name": "IndianOil Citi", "rewards": "Rs 4 per 150 on fuel"}
        ],
        "default": [
            {"name": "HDFC Regalia", "rewards": "4 reward points per ₹150"},
            {"name": "SBI Elite", "rewards": "2X rewards on travel"}
        ]
    }
    
    return {
        "category": spending_category,
        "recommended_cards": cards.get(spending_category.lower(), cards["default"]),
        "note": "Live data requires web scraping or API integration"
    }


def get_search_tools() -> List:
    """Get all search tools (news + misc helpers).

    Note: News agents should prefer `get_news_tools()` to ensure they only use
    web-based news retrieval tools.
    """
    return [
        search_financial_news,
        search_stock_news,
        search_market_trends,
        search_credit_cards
    ]


def get_news_tools() -> List:
    """Tools intended for News Agents only (web search + headlines)."""
    return [
        search_financial_news,
        search_stock_news,
    ]
