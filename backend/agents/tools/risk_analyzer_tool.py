"""
Risk analyzer tools for investment assessment
"""

from typing import List, Dict
from langchain_core.tools import tool


@tool
def calculate_risk_score(
    age: int,
    monthly_income: float,
    monthly_expenses: float,
    existing_investments: float,
    financial_goals: List[str],
    investment_horizon: str
) -> dict:
    """
    Calculate investment risk score.
    
    Args:
        age: User's age
        monthly_income: Monthly income
        monthly_expenses: Monthly expenses
        existing_investments: Current investment portfolio value
        financial_goals: List of financial goals
        investment_horizon: short, medium, or long
        
    Returns:
        Risk score and profile
    """
    score = 50  # Base score
    
    # Age factor (younger = higher risk tolerance)
    if age < 30:
        score += 20
    elif age < 40:
        score += 10
    elif age > 50:
        score -= 15
    
    # Savings rate
    savings_rate = (monthly_income - monthly_expenses) / monthly_income if monthly_income > 0 else 0
    if savings_rate > 0.4:
        score += 15
    elif savings_rate > 0.2:
        score += 5
    elif savings_rate < 0.1:
        score -= 10
    
    # Investment horizon
    horizon_scores = {"short": -15, "medium": 5, "long": 20}
    score += horizon_scores.get(investment_horizon, 0)
    
    # Existing portfolio
    if existing_investments > monthly_income * 24:
        score += 10
    
    # Normalize score
    score = max(0, min(100, score))
    
    # Determine profile
    if score >= 70:
        profile = "aggressive"
        allocation = {"equity": 70, "debt": 20, "gold": 10}
    elif score >= 40:
        profile = "moderate"
        allocation = {"equity": 50, "debt": 40, "gold": 10}
    else:
        profile = "conservative"
        allocation = {"equity": 30, "debt": 60, "gold": 10}
    
    return {
        "risk_score": score,
        "risk_profile": profile,
        "recommended_allocation": allocation,
        "factors": {
            "age_impact": "positive" if age < 40 else "negative",
            "savings_rate": f"{savings_rate * 100:.1f}%",
            "horizon": investment_horizon
        }
    }


@tool
def analyze_portfolio_risk(
    holdings: List[Dict]
) -> dict:
    """
    Analyze risk of current portfolio.
    
    Args:
        holdings: List of holdings with type and value
        
    Returns:
        Portfolio risk analysis
    """
    total_value = sum(h.get("value", 0) for h in holdings)
    
    if total_value == 0:
        return {"error": "Empty portfolio"}
    
    # Calculate allocation
    allocation = {}
    for holding in holdings:
        asset_type = holding.get("type", "other")
        value = holding.get("value", 0)
        allocation[asset_type] = allocation.get(asset_type, 0) + value
    
    # Calculate percentages
    allocation_pct = {
        k: round((v / total_value) * 100, 2)
        for k, v in allocation.items()
    }
    
    # Risk assessment
    equity_pct = allocation_pct.get("equity", 0) + allocation_pct.get("stocks", 0)
    
    if equity_pct > 80:
        risk_level = "high"
        recommendation = "Consider adding debt instruments for stability"
    elif equity_pct > 50:
        risk_level = "moderate"
        recommendation = "Well-balanced portfolio"
    else:
        risk_level = "low"
        recommendation = "Consider adding equity for growth"
    
    # Diversification score
    diversification = min(100, len(allocation) * 20)
    
    return {
        "total_value": total_value,
        "allocation": allocation_pct,
        "risk_level": risk_level,
        "diversification_score": diversification,
        "recommendation": recommendation
    }


@tool
def calculate_investment_capacity(
    monthly_income: float,
    monthly_expenses: float,
    existing_emi: float,
    emergency_fund: float
) -> dict:
    """
    Calculate how much user can invest.
    
    Args:
        monthly_income: Monthly income
        monthly_expenses: Monthly expenses
        existing_emi: Existing EMI obligations
        emergency_fund: Current emergency fund
        
    Returns:
        Investment capacity analysis
    """
    monthly_surplus = monthly_income - monthly_expenses - existing_emi
    required_emergency = monthly_expenses * 6
    
    # Check if emergency fund is adequate
    emergency_gap = max(0, required_emergency - emergency_fund)
    
    if monthly_surplus <= 0:
        return {
            "can_invest": False,
            "reason": "Expenses exceed income",
            "monthly_surplus": monthly_surplus,
            "recommendation": "Focus on reducing expenses first"
        }
    
    # Allocation suggestion
    if emergency_gap > 0:
        emergency_allocation = min(monthly_surplus * 0.5, emergency_gap)
        investment_capacity = monthly_surplus - emergency_allocation
    else:
        emergency_allocation = 0
        investment_capacity = monthly_surplus
    
    return {
        "can_invest": True,
        "monthly_surplus": round(monthly_surplus, 2),
        "emergency_fund_status": "adequate" if emergency_gap == 0 else f"₹{emergency_gap:,.0f} short",
        "suggested_emergency_saving": round(emergency_allocation, 2),
        "investment_capacity": round(investment_capacity, 2),
        "as_percentage_of_income": round((investment_capacity / monthly_income) * 100, 2)
    }


def get_risk_analyzer_tools() -> List:
    """Get all risk analyzer tools."""
    return [
        calculate_risk_score,
        analyze_portfolio_risk,
        calculate_investment_capacity
    ]
