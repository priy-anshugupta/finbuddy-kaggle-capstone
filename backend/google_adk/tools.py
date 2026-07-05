"""
Google ADK Tools Bridge

Wraps existing FinBuddy financial tools (yfinance, calculators, etc.)
into ADK FunctionTool instances so ADK agents can call them.

This demonstrates interoperability between the Google ADK ecosystem
and existing Python toolsets.
"""

from typing import Optional
import yfinance as yf
import pandas as pd
from datetime import datetime

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)

# Lazy import ADK tools to avoid hard failures
try:
    from google.adk.tools import FunctionTool
    _adk_tools_available = True
except ImportError:
    _adk_tools_available = False
    FunctionTool = None  # type: ignore


def get_stock_quote(symbol: str) -> str:
    """
    Get real-time stock quote for an Indian NSE/BSE symbol.

    Args:
        symbol: NSE/BSE symbol (e.g., "RELIANCE.NS", "TCS.NS")

    Returns:
        JSON-like string with price, change, volume, and 52-week range.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1d")
        if hist.empty:
            return f'{{"error": "No data for {symbol}"}}'

        latest = hist.iloc[-1]
        result = {
            "symbol": symbol,
            "price": round(latest["Close"], 2),
            "change": round(latest["Close"] - latest["Open"], 2),
            "change_percent": round((latest["Close"] - latest["Open"]) / latest["Open"] * 100, 2) if latest["Open"] else 0,
            "volume": int(latest["Volume"]),
            "currency": "INR",
            "timestamp": datetime.utcnow().isoformat(),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
        }
        return str(result)
    except Exception as e:
        logger.error("Stock quote failed", symbol=symbol, error=str(e))
        return f'{{"error": "{str(e)}"}}'


def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> str:
    """
    Calculate EMI (Equated Monthly Installment) for Indian loans.

    Args:
        principal: Loan amount in INR (₹)
        annual_rate: Annual interest rate in % (e.g., 8.5)
        tenure_months: Loan duration in months (e.g., 240 for 20 years)

    Returns:
        JSON string with EMI, total interest, and total payment.
    """
    try:
        monthly_rate = annual_rate / (12 * 100)
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = (principal * monthly_rate * (1 + monthly_rate) ** tenure_months) / (
                (1 + monthly_rate) ** tenure_months - 1
            )
        total_payment = emi * tenure_months
        total_interest = total_payment - principal

        result = {
            "principal": round(principal, 2),
            "annual_rate_percent": annual_rate,
            "tenure_months": tenure_months,
            "emi": round(emi, 2),
            "total_interest": round(total_interest, 2),
            "total_payment": round(total_payment, 2),
            "currency": "INR",
        }
        return str(result)
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


def get_inflation_rate() -> str:
    """
    Get latest Indian CPI inflation rate (approximate/reserved value).
    In production, this calls the RBI or World Bank API.

    Returns:
        JSON string with current inflation rate and source.
    """
    # Placeholder: in production, integrate with RBI or World Bank API
    # Using a cached approximate value for demo purposes
    result = {
        "country": "India",
        "cpi_inflation_percent": 4.83,
        "source": "RBI / Ministry of Statistics (approximate)",
        "date": "2025-06",
        "note": "For live data, integrate RBI API or World Bank indicator FP.CPI.TOTL.ZG",
    }
    return str(result)


def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert currency using approximate rates for Indian context.

    Args:
        amount: Amount to convert
        from_currency: Source currency code (e.g., "USD", "INR", "EUR")
        to_currency: Target currency code (e.g., "INR", "USD")

    Returns:
        JSON string with converted amount and rate used.
    """
    # Approximate rates for demonstration (production: use live API)
    rates = {
        "USD": 1.0,
        "INR": 83.5,
        "EUR": 0.92,
        "GBP": 0.79,
        "JPY": 150.0,
    }
    try:
        from_rate = rates.get(from_currency.upper(), 1.0)
        to_rate = rates.get(to_currency.upper(), 1.0)
        converted = amount * (to_rate / from_rate)
        result = {
            "original_amount": amount,
            "from_currency": from_currency.upper(),
            "to_currency": to_currency.upper(),
            "converted_amount": round(converted, 2),
            "rate_used": round(to_rate / from_rate, 4),
            "note": "Approximate rates for demonstration. Use live forex API in production.",
        }
        return str(result)
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


def get_mutual_fund_nav(scheme_code: str) -> str:
    """
    Get latest NAV for an Indian mutual fund scheme.
    In production, integrate with AMFI or CAMS/Karvy API.

    Args:
        scheme_code: AMFI scheme code (e.g., "120437" for HDFC Top 100)

    Returns:
        JSON string with NAV, date, and fund name.
    """
    # Placeholder: production integration with AMFI API
    result = {
        "scheme_code": scheme_code,
        "nav": 845.32,
        "nav_date": "2025-06-25",
        "fund_name": "Sample Fund (use AMFI API for live data)",
        "note": "Integrate https://www.amfiindia.com/spages/NAVAll.txt for production NAV data",
    }
    return str(result)


def build_adk_tools() -> list:
    """
    Build and return a list of ADK FunctionTool instances.

    Returns:
        List of FunctionTool objects ready to be attached to ADK agents.
    """
    if not _adk_tools_available or FunctionTool is None:
        logger.warning("ADK FunctionTool not available. Returning empty tool list.")
        return []

    tools = [
        FunctionTool(func=get_stock_quote),
        FunctionTool(func=calculate_emi),
        FunctionTool(func=get_inflation_rate),
        FunctionTool(func=convert_currency),
        FunctionTool(func=get_mutual_fund_nav),
    ]
    logger.info("ADK tools built", count=len(tools))
    return tools
