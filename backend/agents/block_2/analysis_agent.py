"""
Analysis Agent for risk assessment and profile analysis
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import ANALYSIS_AGENT_PROMPT
from agents.tools.risk_analyzer_tool import get_risk_analyzer_tools
from agents.tools.web_search_tool import search_financial_news, search_market_trends


class AnalysisAgent(BaseAgent):
    """Agent for investment profile and risk analysis."""
    
    def __init__(self, **kwargs):
        # Combine risk analyzer tools with web search for market context
        risk_tools = get_risk_analyzer_tools()
        web_search_tools = [search_financial_news, search_market_trends]
        tools = kwargs.pop("tools", None) or (risk_tools + web_search_tools)
        super().__init__(
            name="analysis_agent",
            description="Analyzes risk tolerance and investment profile",
            system_prompt=ANALYSIS_AGENT_PROMPT,
            tools=tools,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "risk_assessment",
            "cash_flow_analysis",
            "investment_capacity",
            "financial_health_score"
        ]
