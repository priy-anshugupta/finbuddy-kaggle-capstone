"""
FinBuddy AI Agents Package

Multi-agent system for financial assistance powered by GPT-5.1
"""

from agents.base_agent import BaseAgent
from agents.agent_factory import AgentFactory, register_all_agents

from agents.orchestrators import (
    MoneyManagementOrchestrator,
    InvestmentOrchestrator,
    FinancialProductsOrchestrator
)

from agents.block_1 import (
    OCRAgent,
    WatchdogAgent,
    CategorizeAgent,
    InvestmentDetectorAgent,
    MoneyGrowthAgent,
    Block1NewsAgent
)

from agents.block_2 import (
    AnalysisAgent,
    StockAgent,
    InvestmentAgent,
    Block2NewsAgent
)

from agents.block_3 import (
    CreditCardAgent,
    ITRAgent,
    LoanAgent
)

__all__ = [
    # Base
    "BaseAgent",
    "AgentFactory",
    "register_all_agents",
    
    # Orchestrators
    "MoneyManagementOrchestrator",
    "InvestmentOrchestrator",
    "FinancialProductsOrchestrator",
    
    # Block 1
    "OCRAgent",
    "WatchdogAgent",
    "CategorizeAgent",
    "InvestmentDetectorAgent",
    "MoneyGrowthAgent",
    "Block1NewsAgent",
    
    # Block 2
    "AnalysisAgent",
    "StockAgent",
    "InvestmentAgent",
    "Block2NewsAgent",
    
    # Block 3
    "CreditCardAgent",
    "ITRAgent",
    "LoanAgent"
]
