"""
Block 1 agents - Money Management
"""

from agents.block_1.ocr_agent import OCRAgent
from agents.block_1.watchdog_agent import WatchdogAgent
from agents.block_1.categorize_agent import CategorizeAgent
from agents.block_1.investment_detector_agent import InvestmentDetectorAgent
from agents.block_1.money_growth_agent import MoneyGrowthAgent
from agents.block_1.news_agent import Block1NewsAgent

__all__ = [
    "OCRAgent",
    "WatchdogAgent",
    "CategorizeAgent",
    "InvestmentDetectorAgent",
    "MoneyGrowthAgent",
    "Block1NewsAgent"
]
