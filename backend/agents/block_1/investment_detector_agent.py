"""
Investment Detector Agent for identifying recurring payments
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import INVESTMENT_DETECTOR_PROMPT


class InvestmentDetectorAgent(BaseAgent):
    """Agent for detecting recurring payments and investment patterns."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="investment_detector_agent",
            description="Detects SIPs, recurring payments, and investment patterns",
            system_prompt=INVESTMENT_DETECTOR_PROMPT,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "recurring_payment_detection",
            "sip_identification",
            "subscription_tracking",
            "investment_opportunity_detection"
        ]
