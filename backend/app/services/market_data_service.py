"""
Market Data Service for real-time stock and investment data
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import asyncio

import yfinance as yf
import httpx

from app.core.logging import get_logger
from app.core.redis import CacheService
from app.config import settings


logger = get_logger(__name__)


class MarketDataService:
    """
    Service for fetching market data from various sources.
    
    Features:
    - Real-time stock prices
    - Historical data
    - Mutual fund NAV
    - Market indices
    - Caching for performance
    """
    
    # Indian market indices
    INDICES = {
        "nifty50": "^NSEI",
        "sensex": "^BSESN",
        "banknifty": "^NSEBANK",
        "niftyit": "^CNXIT"
    }
    
    # Cache TTLs (in seconds)
    CACHE_TTL_LIVE = 60  # 1 minute for live prices
    CACHE_TTL_HISTORIC = 3600  # 1 hour for historical
    CACHE_TTL_NAV = 86400  # 24 hours for MF NAV
    
    def __init__(self, cache_service: Optional[CacheService] = None):
        self.cache = cache_service
    
    async def get_stock_price(
        self,
        symbol: str,
        exchange: str = "NSE"
    ) -> Dict[str, Any]:
        """
        Get current stock price.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE')
            exchange: Exchange (NSE, BSE)
            
        Returns:
            Current price and related data
        """
        # Format symbol for yfinance
        yf_symbol = f"{symbol}.{'NS' if exchange == 'NSE' else 'BO'}"
        
        # Check cache
        cache_key = f"stock_price:{yf_symbol}"
        if self.cache:
            cached = await self.cache.get_json(cache_key)
            if cached:
                return cached
        
        try:
            ticker = yf.Ticker(yf_symbol)
            info = ticker.info
            
            result = {
                "symbol": symbol,
                "exchange": exchange,
                "name": info.get("longName", symbol),
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "previous_close": info.get("previousClose"),
                "open": info.get("open"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "week_52_high": info.get("fiftyTwoWeekHigh"),
                "week_52_low": info.get("fiftyTwoWeekLow"),
                "dividend_yield": info.get("dividendYield"),
                "timestamp": datetime.utcnow().isoformat()
            }
            
            # Calculate change
            if result["price"] and result["previous_close"]:
                change = result["price"] - result["previous_close"]
                change_pct = (change / result["previous_close"]) * 100
                result["change"] = round(change, 2)
                result["change_percentage"] = round(change_pct, 2)
            
            # Cache result
            if self.cache:
                await self.cache.set_json(cache_key, result, self.CACHE_TTL_LIVE)
            
            return result
            
        except Exception as e:
            logger.error("Failed to fetch stock price", symbol=symbol, error=str(e))
            return {"error": str(e), "symbol": symbol}
    
    async def get_historical_data(
        self,
        symbol: str,
        period: str = "1mo",
        exchange: str = "NSE"
    ) -> Dict[str, Any]:
        """
        Get historical price data.
        
        Args:
            symbol: Stock symbol
            period: Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            exchange: Exchange
            
        Returns:
            Historical data with OHLCV
        """
        yf_symbol = f"{symbol}.{'NS' if exchange == 'NSE' else 'BO'}"
        
        cache_key = f"stock_history:{yf_symbol}:{period}"
        if self.cache:
            cached = await self.cache.get_json(cache_key)
            if cached:
                return cached
        
        try:
            ticker = yf.Ticker(yf_symbol)
            history = ticker.history(period=period)
            
            if history.empty:
                return {"error": "No data available", "symbol": symbol}
            
            # Convert to list of records
            data = []
            for idx, row in history.iterrows():
                data.append({
                    "date": idx.strftime("%Y-%m-%d"),
                    "open": round(row["Open"], 2),
                    "high": round(row["High"], 2),
                    "low": round(row["Low"], 2),
                    "close": round(row["Close"], 2),
                    "volume": int(row["Volume"])
                })
            
            result = {
                "symbol": symbol,
                "period": period,
                "data": data,
                "start_price": data[0]["close"] if data else None,
                "end_price": data[-1]["close"] if data else None,
                "high": max(d["high"] for d in data) if data else None,
                "low": min(d["low"] for d in data) if data else None,
                "avg_volume": int(sum(d["volume"] for d in data) / len(data)) if data else None
            }
            
            # Calculate return
            if result["start_price"] and result["end_price"]:
                result["return_percentage"] = round(
                    ((result["end_price"] - result["start_price"]) / result["start_price"]) * 100, 2
                )
            
            if self.cache:
                await self.cache.set_json(cache_key, result, self.CACHE_TTL_HISTORIC)
            
            return result
            
        except Exception as e:
            logger.error("Failed to fetch history", symbol=symbol, error=str(e))
            return {"error": str(e), "symbol": symbol}
    
    async def get_market_indices(self) -> Dict[str, Any]:
        """Get current values of major market indices."""
        cache_key = "market_indices"
        if self.cache:
            cached = await self.cache.get_json(cache_key)
            if cached:
                return cached
        
        results = {}
        
        for name, symbol in self.INDICES.items():
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                results[name] = {
                    "symbol": symbol,
                    "value": info.get("regularMarketPrice"),
                    "change": info.get("regularMarketChange"),
                    "change_percentage": info.get("regularMarketChangePercent"),
                    "day_high": info.get("dayHigh"),
                    "day_low": info.get("dayLow")
                }
            except Exception as e:
                results[name] = {"error": str(e)}
        
        if self.cache:
            await self.cache.set_json(cache_key, results, self.CACHE_TTL_LIVE)
        
        return results
    
    async def search_stocks(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict[str, str]]:
        """
        Search for stocks by name or symbol.
        
        Args:
            query: Search query
            limit: Max results
            
        Returns:
            List of matching stocks
        """
        # This would ideally use a proper search API
        # For now, using a basic approach
        try:
            # Common Indian stocks for demo
            stocks = [
                {"symbol": "RELIANCE", "name": "Reliance Industries", "exchange": "NSE"},
                {"symbol": "TCS", "name": "Tata Consultancy Services", "exchange": "NSE"},
                {"symbol": "INFY", "name": "Infosys", "exchange": "NSE"},
                {"symbol": "HDFCBANK", "name": "HDFC Bank", "exchange": "NSE"},
                {"symbol": "ICICIBANK", "name": "ICICI Bank", "exchange": "NSE"},
                {"symbol": "SBIN", "name": "State Bank of India", "exchange": "NSE"},
                {"symbol": "WIPRO", "name": "Wipro", "exchange": "NSE"},
                {"symbol": "BHARTIARTL", "name": "Bharti Airtel", "exchange": "NSE"},
                {"symbol": "MARUTI", "name": "Maruti Suzuki", "exchange": "NSE"},
                {"symbol": "TATAMOTORS", "name": "Tata Motors", "exchange": "NSE"},
            ]
            
            query_lower = query.lower()
            matches = [
                s for s in stocks
                if query_lower in s["symbol"].lower() or query_lower in s["name"].lower()
            ]
            
            return matches[:limit]
            
        except Exception as e:
            logger.error("Stock search failed", error=str(e))
            return []
    
    async def get_mutual_fund_nav(
        self,
        scheme_code: str
    ) -> Dict[str, Any]:
        """
        Get mutual fund NAV from AMFI.
        
        Args:
            scheme_code: AMFI scheme code
            
        Returns:
            Current NAV and fund details
        """
        cache_key = f"mf_nav:{scheme_code}"
        if self.cache:
            cached = await self.cache.get_json(cache_key)
            if cached:
                return cached
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"https://api.mfapi.in/mf/{scheme_code}",
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    result = {
                        "scheme_code": scheme_code,
                        "scheme_name": data.get("meta", {}).get("scheme_name"),
                        "fund_house": data.get("meta", {}).get("fund_house"),
                        "scheme_type": data.get("meta", {}).get("scheme_type"),
                        "nav": float(data.get("data", [{}])[0].get("nav", 0)),
                        "date": data.get("data", [{}])[0].get("date"),
                    }
                    
                    if self.cache:
                        await self.cache.set_json(cache_key, result, self.CACHE_TTL_NAV)
                    
                    return result
                else:
                    return {"error": "Failed to fetch NAV", "scheme_code": scheme_code}
                    
        except Exception as e:
            logger.error("MF NAV fetch failed", scheme_code=scheme_code, error=str(e))
            return {"error": str(e), "scheme_code": scheme_code}


# Singleton instance
market_data_service = MarketDataService()
