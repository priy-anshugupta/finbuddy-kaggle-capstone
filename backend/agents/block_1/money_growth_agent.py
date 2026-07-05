"""
Money Growth Agent for spending analysis and financial growth
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import MONEY_GROWTH_PROMPT
from agents.tools.calculator_tool import get_calculator_tools
from agents.tools.web_search_tool import search_financial_news, search_market_trends


class MoneyGrowthAgent(BaseAgent):
    """Agent for analyzing spending and providing growth recommendations."""
    
    def __init__(self, **kwargs):
        # Combine calculator tools with web search for market info
        calc_tools = get_calculator_tools()
        web_search_tools = [search_financial_news, search_market_trends]
        tools = kwargs.pop("tools", None) or (calc_tools + web_search_tools)
        super().__init__(
            name="money_growth_agent",
            description="Analyzes spending patterns and provides growth recommendations",
            system_prompt=MONEY_GROWTH_PROMPT,
            tools=tools,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "spending_analysis",
            "budget_creation",
            "savings_recommendations",
            "financial_projections",
            "goal_tracking"
        ]
