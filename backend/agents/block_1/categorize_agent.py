"""
Categorize Agent for transaction classification
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import CATEGORIZE_AGENT_PROMPT


class CategorizeAgent(BaseAgent):
    """Agent for categorizing transactions."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="categorize_agent",
            description="Categorizes transactions into spending categories",
            system_prompt=CATEGORIZE_AGENT_PROMPT,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "transaction_categorization",
            "merchant_identification",
            "subcategory_assignment",
            "category_learning"
        ]
