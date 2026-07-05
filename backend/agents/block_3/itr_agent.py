"""
ITR Agent for income tax planning
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import ITR_AGENT_PROMPT
from agents.tools.tax_calculator_tool import get_tax_calculator_tools
from agents.tools.web_search_tool import search_financial_news


class ITRAgent(BaseAgent):
    """Agent for income tax calculation and planning."""
    
    def __init__(self, **kwargs):
        # Combine tax calculator tools with web search for latest tax updates
        tax_tools = get_tax_calculator_tools()
        web_search_tools = [search_financial_news]
        tools = kwargs.pop("tools", None) or (tax_tools + web_search_tools)
        super().__init__(
            name="itr_agent",
            description="Calculates income tax and provides tax planning advice",
            system_prompt=ITR_AGENT_PROMPT,
            tools=tools,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "tax_calculation",
            "regime_comparison",
            "deduction_optimization",
            "tax_saving_recommendations"
        ]
