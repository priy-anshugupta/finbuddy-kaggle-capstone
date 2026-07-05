"""
Loan Agent for loan eligibility and comparison
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import LOAN_AGENT_PROMPT
from agents.tools.calculator_tool import get_calculator_tools
from agents.tools.web_search_tool import search_financial_news


class LoanAgent(BaseAgent):
    """Agent for loan eligibility and comparison."""
    
    def __init__(self, **kwargs):
        # Combine calculator tools with web search tools for current rates
        calc_tools = get_calculator_tools()
        web_search_tools = [search_financial_news]
        tools = kwargs.pop("tools", None) or (calc_tools + web_search_tools)
        super().__init__(
            name="loan_agent",
            description="Checks loan eligibility and compares loan options",
            system_prompt=LOAN_AGENT_PROMPT,
            tools=tools,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "loan_eligibility",
            "emi_calculation",
            "loan_comparison",
            "prepayment_analysis"
        ]
