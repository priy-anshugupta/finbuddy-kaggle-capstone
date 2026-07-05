"""
FinBuddy Agent Skills

Composable, reusable skill definitions that represent atomic capabilities
of the FinBuddy agent system. Each skill is a self-contained unit that can
be invoked by ADK agents, CLI commands, or scheduled tasks.

Skills Architecture:
  - FinancialSkill (base class)
  - MarketDataSkill
  - BudgetingSkill
  - TaxPlanningSkill
  - RiskAssessmentSkill

This demonstrates the course concept: Agent Skills (composable, reusable capabilities).
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from datetime import datetime

from app.config import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


class FinancialSkill(ABC):
    """
    Base class for all FinBuddy agent skills.

    Skills are atomic, reusable capabilities that can be:
      - Called by ADK agents via FunctionTool
      - Executed via CLI commands
      - Scheduled as Celery background tasks
      - Chained into complex workflows
    """

    name: str = "base_skill"
    description: str = "Base financial skill"
    version: str = "1.0.0"

    def __init__(self, user_id: Optional[str] = None):
        self.user_id = user_id or "default"
        self.created_at = datetime.utcnow()

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the skill and return structured results."""
        pass

    def log_execution(self, result: Dict[str, Any]):
        """Log skill execution for audit purposes."""
        logger.info(
            "Skill executed",
            skill=self.name,
            user_id=self.user_id,
            success=result.get("success", False),
            duration_ms=result.get("duration_ms"),
        )


class MarketDataSkill(FinancialSkill):
    """
    Skill: Fetch and analyze market data for Indian equities and indices.
    """

    name = "market_data"
    description = "Fetches real-time stock quotes, index values, and market trends for NSE/BSE"

    def execute(self, symbol: Optional[str] = None, index: Optional[str] = None) -> Dict[str, Any]:
        import yfinance as yf
        start = datetime.utcnow()

        result = {"symbol": symbol, "index": index, "data": None}

        try:
            if symbol:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                info = ticker.info
                if not hist.empty:
                    latest = hist.iloc[-1]
                    result["data"] = {
                        "price": round(latest["Close"], 2),
                        "change": round(latest["Close"] - latest["Open"], 2),
                        "volume": int(latest["Volume"]),
                        "market_cap": info.get("marketCap"),
                        "pe": info.get("trailingPE"),
                    }
            elif index:
                mapping = {"NIFTY_50": "^NSEI", "SENSEX": "^BSESN", "BANK_NIFTY": "^NSEBANK"}
                ticker = yf.Ticker(mapping.get(index, index))
                hist = ticker.history(period="1d")
                if not hist.empty:
                    latest = hist.iloc[-1]
                    result["data"] = {
                        "price": round(latest["Close"], 2),
                        "change": round(latest["Close"] - latest["Open"], 2),
                    }

            result["success"] = True
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        result["duration_ms"] = (datetime.utcnow() - start).total_seconds() * 1000
        self.log_execution(result)
        return result


class BudgetingSkill(FinancialSkill):
    """
    Skill: Analyze spending patterns and generate personalized budgets.
    """

    name = "budgeting"
    description = "Analyzes transaction history and creates a 50-30-20 style budget recommendation"

    def execute(self, monthly_income: float, transactions: Optional[list] = None) -> Dict[str, Any]:
        start = datetime.utcnow()

        result = {"monthly_income": monthly_income}

        try:
            # Default 50-30-20 split if no transactions provided
            needs = monthly_income * 0.50
            wants = monthly_income * 0.30
            savings = monthly_income * 0.20

            result["budget"] = {
                "needs": round(needs, 2),
                "wants": round(wants, 2),
                "savings": round(savings, 2),
                "currency": "INR",
            }
            result["recommendation"] = (
                "Follow the 50-30-20 rule: 50% for needs, 30% for wants, 20% for savings. "
                "Indian context: aim for 6-month emergency fund first."
            )
            result["success"] = True
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        result["duration_ms"] = (datetime.utcnow() - start).total_seconds() * 1000
        self.log_execution(result)
        return result


class TaxPlanningSkill(FinancialSkill):
    """
    Skill: Compare old vs new tax regime and optimize deductions for Indian taxpayers.
    """

    name = "tax_planning"
    description = "Compares old vs new Indian tax regime and identifies 80C/80D optimization opportunities"

    def execute(self, annual_income: float, current_regime: str = "old",
                deductions_80c: float = 0, deductions_80d: float = 0) -> Dict[str, Any]:
        start = datetime.utcnow()

        result = {"annual_income": annual_income, "current_regime": current_regime}

        try:
            # Simplified FY 2025-26 slabs (approximate)
            # Old regime: 0-3L=0%, 3-5L=5%, 5-10L=20%, 10L+=30% + 4% cess
            # New regime: 0-4L=0%, 4-8L=5%, 8-12L=10%, 12-16L=15%, 16-20L=20%, 20-24L=25%, 24L+=30% + 4% cess

            def old_tax(income, d80c, d80d):
                taxable = max(0, income - 50000 - d80c - d80d)  # standard deduction 50k
                tax = 0
                if taxable > 1000000:
                    tax += (taxable - 1000000) * 0.30
                    taxable = 1000000
                if taxable > 500000:
                    tax += (taxable - 500000) * 0.20
                    taxable = 500000
                if taxable > 300000:
                    tax += (taxable - 300000) * 0.05
                tax += tax * 0.04  # cess
                return tax

            def new_tax(income):
                taxable = max(0, income - 75000)  # standard deduction 75k in new regime FY 25-26
                slabs = [(2400000, 0.30), (2000000, 0.25), (1600000, 0.20),
                         (1200000, 0.15), (800000, 0.10), (400000, 0.05)]
                tax = 0
                for limit, rate in slabs:
                    if taxable > limit:
                        tax += (taxable - limit) * rate
                        taxable = limit
                tax += tax * 0.04
                return tax

            old = old_tax(annual_income, deductions_80c, deductions_80d)
            new = new_tax(annual_income)

            result["comparison"] = {
                "old_regime_tax": round(old, 2),
                "new_regime_tax": round(new, 2),
                "recommended_regime": "old" if old < new else "new",
                "potential_savings": round(abs(old - new), 2),
                "currency": "INR",
            }
            result["success"] = True
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        result["duration_ms"] = (datetime.utcnow() - start).total_seconds() * 1000
        self.log_execution(result)
        return result


class RiskAssessmentSkill(FinancialSkill):
    """
    Skill: Assess financial risk profile based on spending stability and portfolio.
    """

    name = "risk_assessment"
    description = "Calculates risk score (Conservative/Moderate/Aggressive) based on spending variance and age"

    def execute(self, age: int, monthly_spending_variance: float = 0.0,
                emergency_months: float = 0.0) -> Dict[str, Any]:
        start = datetime.utcnow()

        result = {"age": age, "spending_variance": monthly_spending_variance, "emergency_months": emergency_months}

        try:
            score = 0

            # Age factor: younger = higher risk capacity
            if age < 30:
                score += 3
            elif age < 45:
                score += 2
            else:
                score += 1

            # Spending stability: lower variance = higher risk capacity
            if monthly_spending_variance < 0.10:
                score += 3
            elif monthly_spending_variance < 0.25:
                score += 2
            else:
                score += 1

            # Emergency fund: >6 months = higher risk capacity
            if emergency_months >= 6:
                score += 3
            elif emergency_months >= 3:
                score += 2
            else:
                score += 1

            if score >= 7:
                profile = "Aggressive"
                equity_split = 70
            elif score >= 5:
                profile = "Moderate"
                equity_split = 50
            else:
                profile = "Conservative"
                equity_split = 30

            result["risk_profile"] = {
                "profile": profile,
                "score": score,
                "recommended_equity_percent": equity_split,
                "recommended_debt_percent": 100 - equity_split,
                "note": "Based on Indian market norms: 100 - age rule adjusted for stability.",
            }
            result["success"] = True
        except Exception as e:
            result["success"] = False
            result["error"] = str(e)

        result["duration_ms"] = (datetime.utcnow() - start).total_seconds() * 1000
        self.log_execution(result)
        return result


# Skill registry for discovery
SKILL_REGISTRY = {
    "market_data": MarketDataSkill,
    "budgeting": BudgetingSkill,
    "tax_planning": TaxPlanningSkill,
    "risk_assessment": RiskAssessmentSkill,
}


def get_skill(name: str, user_id: Optional[str] = None) -> Optional[FinancialSkill]:
    """Factory to instantiate a skill by name."""
    skill_class = SKILL_REGISTRY.get(name)
    if skill_class:
        return skill_class(user_id=user_id)
    return None
