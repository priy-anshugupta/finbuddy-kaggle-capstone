"""
Stock Agent for equity research
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import STOCK_AGENT_PROMPT
from agents.tools.market_data_tool import get_market_data_tools
from agents.tools.web_search_tool import search_financial_news, search_stock_news


class StockAgent(BaseAgent):
    """Agent for stock and equity research."""
    
    def __init__(self, **kwargs):
        # Combine market data tools with web search tools
        market_tools = get_market_data_tools()
        web_search_tools = [search_financial_news, search_stock_news]
        tools = kwargs.pop("tools", None) or (market_tools + web_search_tools)
        super().__init__(
            name="stock_agent",
            description="Researches stocks, mutual funds, and ETFs",
            system_prompt=STOCK_AGENT_PROMPT,
            tools=tools,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "stock_research",
            "mutual_fund_analysis",
            "etf_comparison",
            "technical_analysis",
            "fundamental_analysis"
        ]
