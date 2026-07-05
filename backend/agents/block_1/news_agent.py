"""
News Agent (Block 1) for personal finance news
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import NEWS_AGENT_BLOCK1_PROMPT
from agents.tools.web_search_tool import get_news_tools


class Block1NewsAgent(BaseAgent):
    """Agent for personal finance and spending-related news."""
    
    def __init__(self, **kwargs):
        tools = kwargs.pop("tools", None) or get_news_tools()
        super().__init__(
            name="block1_news_agent",
            description="Provides personal finance news and trends",
            system_prompt=NEWS_AGENT_BLOCK1_PROMPT,
            tools=tools,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "personal_finance_news",
            "inflation_updates",
            "deals_and_discounts",
            "spending_trends"
        ]
