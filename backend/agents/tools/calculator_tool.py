"""
Calculator tools for financial calculations
"""

from typing import List
from langchain_core.tools import tool


@tool
def calculate_emi(principal: float, annual_rate: float, tenure_months: int) -> dict:
    """
    Calculate EMI (Equated Monthly Installment) for a loan.
    
    Args:
        principal: Loan principal amount
        annual_rate: Annual interest rate (e.g., 12 for 12%)
        tenure_months: Loan tenure in months
        
    Returns:
        EMI amount and total payment details
    """
    monthly_rate = annual_rate / 100 / 12
    
    if monthly_rate == 0:
        emi = principal / tenure_months
    else:
        emi = principal * monthly_rate * ((1 + monthly_rate) ** tenure_months) / \
              (((1 + monthly_rate) ** tenure_months) - 1)
    
    total_payment = emi * tenure_months
    total_interest = total_payment - principal
    
    return {
        "emi": round(emi, 2),
        "total_payment": round(total_payment, 2),
        "total_interest": round(total_interest, 2),
        "principal": principal,
        "tenure_months": tenure_months,
        "annual_rate": annual_rate
    }


@tool
def calculate_compound_interest(
    principal: float,
    annual_rate: float,
    years: int,
    compounds_per_year: int = 12
) -> dict:
    """
    Calculate compound interest.
    
    Args:
        principal: Initial investment
        annual_rate: Annual interest rate (e.g., 8 for 8%)
        years: Investment duration in years
        compounds_per_year: Compounding frequency (12 for monthly)
        
    Returns:
        Final amount and interest earned
    """
    rate = annual_rate / 100
    final_amount = principal * (1 + rate / compounds_per_year) ** (compounds_per_year * years)
    interest_earned = final_amount - principal
    
    return {
        "final_amount": round(final_amount, 2),
        "interest_earned": round(interest_earned, 2),
        "principal": principal,
        "annual_rate": annual_rate,
        "years": years
    }


@tool
def calculate_sip_returns(
    monthly_investment: float,
    annual_rate: float,
    years: int
) -> dict:
    """
    Calculate SIP (Systematic Investment Plan) returns.
    
    Args:
        monthly_investment: Monthly SIP amount
        annual_rate: Expected annual return rate (e.g., 12 for 12%)
        years: Investment duration in years
        
    Returns:
        Total invested, final value, and returns
    """
    months = years * 12
    monthly_rate = annual_rate / 100 / 12
    
    if monthly_rate == 0:
        future_value = monthly_investment * months
    else:
        future_value = monthly_investment * ((1 + monthly_rate) ** months - 1) / monthly_rate * (1 + monthly_rate)
    
    total_invested = monthly_investment * months
    returns = future_value - total_invested
    
    return {
        "future_value": round(future_value, 2),
        "total_invested": round(total_invested, 2),
        "returns": round(returns, 2),
        "returns_percentage": round((returns / total_invested) * 100, 2),
        "monthly_investment": monthly_investment,
        "years": years
    }


@tool
def calculate_goal_sip(
    target_amount: float,
    annual_rate: float,
    years: int
) -> dict:
    """
    Calculate required monthly SIP to reach a goal.
    
    Args:
        target_amount: Target amount to achieve
        annual_rate: Expected annual return rate
        years: Time horizon in years
        
    Returns:
        Required monthly SIP amount
    """
    months = years * 12
    monthly_rate = annual_rate / 100 / 12
    
    if monthly_rate == 0:
        monthly_sip = target_amount / months
    else:
        monthly_sip = target_amount * monthly_rate / ((1 + monthly_rate) ** months - 1) / (1 + monthly_rate)
    
    return {
        "required_monthly_sip": round(monthly_sip, 2),
        "target_amount": target_amount,
        "years": years,
        "annual_rate": annual_rate,
        "total_investment": round(monthly_sip * months, 2)
    }


@tool
def calculate_fd_maturity(
    principal: float,
    annual_rate: float,
    years: int,
    compounding: str = "quarterly"
) -> dict:
    """
    Calculate Fixed Deposit maturity amount.
    
    Args:
        principal: FD principal amount
        annual_rate: Annual interest rate
        years: FD tenure in years
        compounding: Compounding frequency (quarterly, monthly, yearly)
        
    Returns:
        Maturity amount and interest earned
    """
    compounds = {"monthly": 12, "quarterly": 4, "yearly": 1}
    n = compounds.get(compounding, 4)
    
    rate = annual_rate / 100
    maturity = principal * (1 + rate / n) ** (n * years)
    interest = maturity - principal
    
    return {
        "maturity_amount": round(maturity, 2),
        "interest_earned": round(interest, 2),
        "principal": principal,
        "annual_rate": annual_rate,
        "years": years
    }


def get_calculator_tools() -> List:
    """Get all calculator tools."""
    return [
        calculate_emi,
        calculate_compound_interest,
        calculate_sip_returns,
        calculate_goal_sip,
        calculate_fd_maturity
    ]
