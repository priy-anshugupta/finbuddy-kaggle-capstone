"""
Tax calculator tools for Indian income tax
"""

from typing import List
from langchain_core.tools import tool


@tool
def calculate_income_tax_old_regime(
    gross_income: float,
    deductions_80c: float = 0,
    deductions_80d: float = 0,
    hra_exemption: float = 0,
    other_deductions: float = 0
) -> dict:
    """
    Calculate income tax under Old Regime (FY 2024-25).
    
    Args:
        gross_income: Total gross income
        deductions_80c: Section 80C deductions (max 1.5L)
        deductions_80d: Section 80D health insurance (max 75K)
        hra_exemption: HRA exemption amount
        other_deductions: Other eligible deductions
        
    Returns:
        Tax calculation breakdown
    """
    # Apply limits
    deductions_80c = min(deductions_80c, 150000)
    deductions_80d = min(deductions_80d, 75000)
    
    # Standard deduction for salaried
    standard_deduction = 50000
    
    total_deductions = deductions_80c + deductions_80d + hra_exemption + other_deductions + standard_deduction
    taxable_income = max(0, gross_income - total_deductions)
    
    # Old regime slabs
    tax = 0
    if taxable_income > 1000000:
        tax += (taxable_income - 1000000) * 0.30
        taxable_income = 1000000
    if taxable_income > 500000:
        tax += (taxable_income - 500000) * 0.20
        taxable_income = 500000
    if taxable_income > 250000:
        tax += (taxable_income - 250000) * 0.05
    
    # Health and education cess
    cess = tax * 0.04
    total_tax = tax + cess
    
    return {
        "regime": "old",
        "gross_income": gross_income,
        "total_deductions": total_deductions,
        "taxable_income": max(0, gross_income - total_deductions),
        "tax_before_cess": round(tax, 2),
        "cess": round(cess, 2),
        "total_tax": round(total_tax, 2),
        "effective_rate": round((total_tax / gross_income) * 100, 2) if gross_income > 0 else 0
    }


@tool
def calculate_income_tax_new_regime(gross_income: float) -> dict:
    """
    Calculate income tax under New Regime (FY 2024-25).
    
    Args:
        gross_income: Total gross income
        
    Returns:
        Tax calculation under new regime
    """
    # Standard deduction for salaried
    standard_deduction = 75000
    taxable_income = max(0, gross_income - standard_deduction)
    
    # New regime slabs (FY 2024-25)
    tax = 0
    remaining = taxable_income
    
    slabs = [
        (300000, 0),
        (400000, 0.05),
        (700000, 0.10),
        (1000000, 0.15),
        (1200000, 0.20),
        (1500000, 0.25),
        (float('inf'), 0.30)
    ]
    
    prev_limit = 0
    for limit, rate in slabs:
        if remaining <= 0:
            break
        slab_amount = min(remaining, limit - prev_limit)
        tax += slab_amount * rate
        remaining -= slab_amount
        prev_limit = limit
    
    # Rebate u/s 87A for income up to 7L
    if taxable_income <= 700000:
        tax = 0
    
    cess = tax * 0.04
    total_tax = tax + cess
    
    return {
        "regime": "new",
        "gross_income": gross_income,
        "standard_deduction": standard_deduction,
        "taxable_income": taxable_income,
        "tax_before_cess": round(tax, 2),
        "cess": round(cess, 2),
        "total_tax": round(total_tax, 2),
        "effective_rate": round((total_tax / gross_income) * 100, 2) if gross_income > 0 else 0
    }


@tool
def compare_tax_regimes(
    gross_income: float,
    deductions_80c: float = 0,
    deductions_80d: float = 0,
    hra_exemption: float = 0,
    other_deductions: float = 0
) -> dict:
    """
    Compare old and new tax regimes.
    
    Args:
        gross_income: Total gross income
        deductions_80c: Section 80C deductions
        deductions_80d: Section 80D deductions
        hra_exemption: HRA exemption
        other_deductions: Other deductions
        
    Returns:
        Comparison of both regimes with recommendation
    """
    old = calculate_income_tax_old_regime.invoke({
        "gross_income": gross_income,
        "deductions_80c": deductions_80c,
        "deductions_80d": deductions_80d,
        "hra_exemption": hra_exemption,
        "other_deductions": other_deductions
    })
    
    new = calculate_income_tax_new_regime.invoke({"gross_income": gross_income})
    
    savings = old["total_tax"] - new["total_tax"]
    recommended = "new" if savings > 0 else "old"
    
    return {
        "old_regime": old,
        "new_regime": new,
        "difference": abs(savings),
        "recommended_regime": recommended,
        "recommendation": f"{'New' if recommended == 'new' else 'Old'} regime saves ₹{abs(savings):,.2f}"
    }


@tool
def calculate_80c_optimization(
    current_investments: dict,
    available_for_investment: float
) -> dict:
    """
    Optimize Section 80C investments.
    
    Args:
        current_investments: Dict of current 80C investments
        available_for_investment: Amount available for additional investment
        
    Returns:
        Optimization suggestions
    """
    max_80c = 150000
    total_current = sum(current_investments.values())
    remaining_limit = max(0, max_80c - total_current)
    
    suggestions = []
    
    if remaining_limit > 0:
        invest_amount = min(remaining_limit, available_for_investment)
        
        # Prioritized investment options
        if invest_amount >= 50000:
            suggestions.append({
                "instrument": "ELSS Mutual Funds",
                "amount": min(invest_amount, 50000),
                "reason": "Tax saving + wealth creation, 3-year lock-in"
            })
        
        if invest_amount >= 12000:
            suggestions.append({
                "instrument": "PPF",
                "amount": min(invest_amount, 12000),
                "reason": "Safe, tax-free returns, 15-year tenure"
            })
    
    return {
        "current_80c": total_current,
        "remaining_limit": remaining_limit,
        "suggestions": suggestions,
        "potential_tax_saved": remaining_limit * 0.30 if total_current < max_80c else 0
    }


def get_tax_calculator_tools() -> List:
    """Get all tax calculator tools."""
    return [
        calculate_income_tax_old_regime,
        calculate_income_tax_new_regime,
        compare_tax_regimes,
        calculate_80c_optimization
    ]
