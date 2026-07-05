"""
OCR Agent for extracting transaction data from documents
"""

from typing import List
from agents.base_agent import BaseAgent
from agents.prompts.system_prompts import OCR_AGENT_PROMPT


class OCRAgent(BaseAgent):
    """Agent for OCR-based transaction extraction."""
    
    def __init__(self, **kwargs):
        super().__init__(
            name="ocr_agent",
            description="Extracts transaction data from SMS, receipts, and bank statements",
            system_prompt=OCR_AGENT_PROMPT,
            **kwargs
        )
    
    def get_capabilities(self) -> List[str]:
        return [
            "sms_parsing",
            "receipt_ocr",
            "bank_statement_parsing",
            "transaction_extraction"
        ]
