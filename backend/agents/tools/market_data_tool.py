"""
Market data tools for stock and investment research
"""

from typing import List, Optional
from langchain_core.tools import tool
import yfinance as yf


@tool
def get_stock_price(symbol: str) -> dict:
    """
    Get current stock price and basic info.
    
    Args:
        symbol: Stock symbol (e.g., 'RELIANCE.NS' for NSE)
        
    Returns:
        Current price and basic stock information
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "current_price": info.get("currentPrice", info.get("regularMarketPrice")),
            "previous_close": info.get("previousClose"),
            "day_high": info.get("dayHigh"),
            "day_low": info.get("dayLow"),
            "52_week_high": info.get("fiftyTwoWeekHigh"),
            "52_week_low": info.get("fiftyTwoWeekLow"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "dividend_yield": info.get("dividendYield"),
            "sector": info.get("sector"),
            "industry": info.get("industry")
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}


@tool
def get_stock_history(
    symbol: str,
    period: str = "1mo"
) -> dict:
    """
    Get historical stock data.
    
    Args:
        symbol: Stock symbol
        period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y)
        
    Returns:
        Historical price data summary
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)
        
        if hist.empty:
            return {"error": "No data available", "symbol": symbol}
        
        return {
            "symbol": symbol,
            "period": period,
            "start_price": round(hist['Close'].iloc[0], 2),
            "end_price": round(hist['Close'].iloc[-1], 2),
            "high": round(hist['High'].max(), 2),
            "low": round(hist['Low'].min(), 2),
            "avg_volume": int(hist['Volume'].mean()),
            "return_percentage": round(
                ((hist['Close'].iloc[-1] - hist['Close'].iloc[0]) / hist['Close'].iloc[0]) * 100, 2
            )
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}


@tool
def get_mutual_fund_info(symbol: str) -> dict:
    """
    Get mutual fund information.
    
    Args:
        symbol: Fund symbol
        
    Returns:
        Fund information and performance
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        return {
            "symbol": symbol,
            "name": info.get("longName", symbol),
            "nav": info.get("navPrice"),
            "category": info.get("category"),
            "ytd_return": info.get("ytdReturn"),
            "3_year_return": info.get("threeYearAverageReturn"),
            "5_year_return": info.get("fiveYearAverageReturn"),
            "expense_ratio": info.get("annualReportExpenseRatio"),
            "total_assets": info.get("totalAssets")
        }
    except Exception as e:
        return {"error": str(e), "symbol": symbol}


@tool
def compare_stocks(symbols: List[str]) -> dict:
    """
    Compare multiple stocks.
    
    Args:
        symbols: List of stock symbols to compare
        
    Returns:
        Comparison of key metrics
    """
    results = []
    
    for symbol in symbols[:5]:  # Limit to 5 stocks
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            results.append({
                "symbol": symbol,
                "name": info.get("longName", symbol),
                "price": info.get("currentPrice", info.get("regularMarketPrice")),
                "pe_ratio": info.get("trailingPE"),
                "pb_ratio": info.get("priceToBook"),
                "market_cap": info.get("marketCap"),
                "dividend_yield": info.get("dividendYield"),
                "52w_return": info.get("52WeekChange")
            })
        except Exception:
            results.append({"symbol": symbol, "error": "Failed to fetch data"})
    
    return {"comparison": results}


def get_market_data_tools() -> List:
    """Get all market data tools."""
    return [
        get_stock_price,
        get_stock_history,
        get_mutual_fund_info,
        compare_stocks
    ]
