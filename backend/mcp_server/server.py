"""
FinBuddy MCP Financial Data Server

An MCP (Model Context Protocol) server that exposes financial data tools
for use by any MCP-compatible client, including FinBuddy's ADK agents.

Tools exposed:
  - get_stock_quote(symbol)         -> Real-time NSE/BSE stock data via yfinance
  - get_mutual_fund_nav(code)      -> Latest NAV for Indian mutual funds
  - calculate_emi(p, r, n)       -> EMI calculator for Indian loans
  - get_inflation_rate()           -> Indian CPI inflation (approximate)
  - convert_currency(a, fr, to)    -> Currency conversion
  - calculate_compound_interest()  -> FD/RD/PPF maturity projection

Run:  python -m mcp_server.server
Or:   uvicorn mcp_server.server:app --port 8001
"""

from mcp.server.fastmcp import FastMCP
import yfinance as yf
from datetime import datetime

# Create the MCP server
mcp = FastMCP("finbuddy_finance")


@mcp.tool()
def get_stock_quote(symbol: str) -> str:
    """
    Get real-time stock quote for an Indian NSE/BSE symbol.

    Args:
        symbol: NSE/BSE ticker (e.g., "RELIANCE.NS", "TCS.NS", "INFY.NS")

    Returns:
        JSON string with price, change, volume, 52-week high/low.
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
            "change_percent": round(
                (latest["Close"] - latest["Open"]) / latest["Open"] * 100, 2
            ) if latest["Open"] else 0,
            "volume": int(latest["Volume"]),
            "currency": info.get("currency", "INR"),
            "timestamp": datetime.utcnow().isoformat(),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
        }
        return str(result)
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


@mcp.tool()
def get_mutual_fund_nav(scheme_code: str) -> str:
    """
    Get latest NAV for an Indian mutual fund scheme.

    Args:
        scheme_code: AMFI scheme code (e.g., "120437")

    Returns:
        JSON string with NAV, date, and fund name.
    """
    # Production: integrate with AMFI India API
    # https://www.amfiindia.com/spages/NAVAll.txt
    result = {
        "scheme_code": scheme_code,
        "nav": 845.32,
        "nav_date": "2025-06-25",
        "fund_name": "Sample Fund (integrate AMFI API for production)",
        "source": "AMFI India (placeholder)",
    }
    return str(result)


@mcp.tool()
def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> str:
    """
    Calculate EMI for Indian loans.

    Args:
        principal: Loan amount in INR
        annual_rate: Annual interest rate in % (e.g., 8.5)
        tenure_months: Duration in months (e.g., 240 for 20 years)

    Returns:
        JSON string with EMI, total interest, and total payment.
    """
    try:
        monthly_rate = annual_rate / (12 * 100)
        if monthly_rate == 0:
            emi = principal / tenure_months
        else:
            emi = (
                principal * monthly_rate * (1 + monthly_rate) ** tenure_months
            ) / ((1 + monthly_rate) ** tenure_months - 1)

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


@mcp.tool()
def get_inflation_rate() -> str:
    """
    Get approximate Indian CPI inflation rate.

    Returns:
        JSON string with inflation rate and source note.
    """
    result = {
        "country": "India",
        "cpi_inflation_percent": 4.83,
        "source": "RBI / Ministry of Statistics (approximate for demo)",
        "date": "2025-06",
        "note": "For live data, integrate RBI API or World Bank indicator FP.CPI.TOTL.ZG",
    }
    return str(result)


@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """
    Convert currency (approximate rates for demo).

    Args:
        amount: Amount to convert
        from_currency: Source code (USD, INR, EUR, GBP, JPY)
        to_currency: Target code (USD, INR, EUR, GBP, JPY)

    Returns:
        JSON string with converted amount and rate used.
    """
    rates = {"USD": 1.0, "INR": 83.5, "EUR": 0.92, "GBP": 0.79, "JPY": 150.0}
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


@mcp.tool()
def calculate_compound_interest(
    principal: float, annual_rate: float, years: int, compound_frequency: int = 1
) -> str:
    """
    Calculate maturity value for Indian fixed-income instruments (FD, PPF, RD).

    Args:
        principal: Initial investment in INR
        annual_rate: Annual interest rate in %
        years: Investment duration in years
        compound_frequency: Times per year interest compounds (1=annual, 4=quarterly, 12=monthly)

    Returns:
        JSON string with maturity value, total interest, and effective annual yield.
    """
    try:
        rate_per_period = (annual_rate / 100) / compound_frequency
        total_periods = years * compound_frequency
        maturity = principal * (1 + rate_per_period) ** total_periods
        total_interest = maturity - principal
        effective_yield = ((maturity / principal) ** (1 / years) - 1) * 100

        result = {
            "principal": round(principal, 2),
            "annual_rate_percent": annual_rate,
            "years": years,
            "compound_frequency": compound_frequency,
            "maturity_value": round(maturity, 2),
            "total_interest": round(total_interest, 2),
            "effective_annual_yield_percent": round(effective_yield, 2),
            "currency": "INR",
        }
        return str(result)
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


@mcp.tool()
def get_market_indices() -> str:
    """
    Get current values for major Indian market indices.

    Returns:
        JSON string with Nifty 50, Sensex, and Bank Nifty data.
    """
    try:
        indices = {
            "NIFTY_50": yf.Ticker("^NSEI"),
            "SENSEX": yf.Ticker("^BSESN"),
            "BANK_NIFTY": yf.Ticker("^NSEBANK"),
        }
        result = {}
        for name, ticker in indices.items():
            hist = ticker.history(period="1d")
            if not hist.empty:
                latest = hist.iloc[-1]
                result[name] = {
                    "price": round(latest["Close"], 2),
                    "change": round(latest["Close"] - latest["Open"], 2),
                    "change_percent": round(
                        (latest["Close"] - latest["Open"]) / latest["Open"] * 100, 2
                    ) if latest["Open"] else 0,
                    "volume": int(latest["Volume"]),
                }
            else:
                result[name] = {"error": "No data"}
        result["timestamp"] = datetime.utcnow().isoformat()
        result["currency"] = "INR"
        return str(result)
    except Exception as e:
        return f'{{"error": "{str(e)}"}}'


if __name__ == "__main__":
    # Run with stdio transport (for MCP clients like Claude Desktop)
    mcp.run(transport="stdio")
