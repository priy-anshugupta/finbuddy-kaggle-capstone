"""
Watchdog Agent for transaction validation and anomaly detection
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import WATCHDOG_AGENT_PROMPT


class WatchdogAgent(BaseAgent):
    """Agent for validating transactions and detecting anomalies."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="watchdog_agent",
            description="Validates transactions and detects anomalies/fraud",
            system_prompt=WATCHDOG_AGENT_PROMPT,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "duplicate_detection",
            "anomaly_detection",
            "fraud_detection",
            "missing_entry_identification",
            "transaction_validation"
        ]
