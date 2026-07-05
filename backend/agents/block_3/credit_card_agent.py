"""
Credit Card Agent for card recommendations
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import CREDIT_CARD_AGENT_PROMPT
from agents.tools.web_search_tool import get_search_tools


class CreditCardAgent(BaseAgent):
    """Agent for credit card recommendations and comparison."""
    
    def __init__(self, **kwargs):
        tools = kwargs.pop("tools", None) or get_search_tools()
        super().__init__(
            name="credit_card_agent",
            description="Recommends and compares credit cards",
            system_prompt=CREDIT_CARD_AGENT_PROMPT,
            tools=tools,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "credit_card_recommendations",
            "rewards_optimization",
            "fee_comparison",
            "benefits_analysis"
        ]
