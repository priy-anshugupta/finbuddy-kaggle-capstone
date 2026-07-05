"""
Dashboard API endpoints
"""

from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, CurrentUser
from app.models.transaction import Transaction, TransactionType, TransactionCategory
from app.models.investment import Investment, InvestmentStatus


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
async def get_dashboard_summary(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get dashboard summary with key financial metrics."""
    # Get current month date range
    today = datetime.utcnow()
    first_of_month = today.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    # Previous month
    if today.month == 1:
        first_of_prev_month = today.replace(year=today.year - 1, month=12, day=1)
    else:
        first_of_prev_month = today.replace(month=today.month - 1, day=1)
    
    # Get transactions for current month
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .where(Transaction.transaction_date >= first_of_month)
    )
    current_month_txns = result.scalars().all()
    
    # Get transactions for previous month
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .where(Transaction.transaction_date >= first_of_prev_month)
        .where(Transaction.transaction_date < first_of_month)
    )
    prev_month_txns = result.scalars().all()
    
    # Calculate current month metrics
    current_income = sum(t.amount for t in current_month_txns if t.transaction_type == TransactionType.CREDIT)
    current_expenses = sum(t.amount for t in current_month_txns if t.transaction_type == TransactionType.DEBIT)
    current_savings = current_income - current_expenses
    
    # Calculate previous month metrics
    prev_income = sum(t.amount for t in prev_month_txns if t.transaction_type == TransactionType.CREDIT)
    prev_expenses = sum(t.amount for t in prev_month_txns if t.transaction_type == TransactionType.DEBIT)
    
    # Get investments
    result = await db.execute(
        select(Investment)
        .where(Investment.user_id == current_user.id)
        .where(Investment.status == InvestmentStatus.ACTIVE)
    )
    investments = result.scalars().all()
    
    total_invested = sum(i.invested_amount for i in investments)
    current_value = sum(i.current_value or i.invested_amount for i in investments)
    
    # Calculate spending by category
    spending_by_category = {}
    for t in current_month_txns:
        if t.transaction_type == TransactionType.DEBIT:
            cat = t.category.value
            spending_by_category[cat] = spending_by_category.get(cat, 0) + t.amount
    
    return {
        "total_balance": current_savings + current_value,
        "monthly_income": float(current_income),
        "monthly_expenses": float(current_expenses),
        "savings_rate": float((current_savings / current_income * 100) if current_income > 0 else 0),
        "investment_value": float(current_value),
        "net_worth": float(current_value + current_savings),
        "current_month": {
            "income": float(current_income),
            "expenses": float(current_expenses),
            "savings": float(current_savings),
            "savings_rate": float((current_savings / current_income * 100) if current_income > 0 else 0)
        },
        "previous_month": {
            "income": float(prev_income),
            "expenses": float(prev_expenses),
            "savings": float(prev_income - prev_expenses)
        },
        "changes": {
            "income_change": float(((current_income - prev_income) / prev_income * 100) if prev_income > 0 else 0),
            "expense_change": float(((current_expenses - prev_expenses) / prev_expenses * 100) if prev_expenses > 0 else 0)
        },
        "investments": {
            "total_invested": float(total_invested),
            "current_value": float(current_value),
            "returns": float(current_value - total_invested),
            "returns_percentage": float(((current_value - total_invested) / total_invested * 100) if total_invested > 0 else 0)
        },
        "spending_by_category": {k: float(v) for k, v in spending_by_category.items()}
    }


@router.get("/spending-trends")
async def get_spending_trends(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    months: int = 6,
    period: str = "month"
):
    """Get spending trends over the past months."""
    today = datetime.utcnow()
    start_date = today - timedelta(days=months * 30)
    
    result = await db.execute(
        select(Transaction)
        .where(Transaction.user_id == current_user.id)
        .where(Transaction.transaction_date >= start_date)
        .order_by(Transaction.transaction_date)
    )
    transactions = result.scalars().all()
    
    # Group by month
    monthly_data = {}
    for t in transactions:
        month_key = t.transaction_date.strftime("%Y-%m")
        month_label = t.transaction_date.strftime("%b %Y")
        if month_key not in monthly_data:
            monthly_data[month_key] = {
                "month": month_label,
                "income": 0, 
                "expenses": 0, 
                "by_category": {}
            }
        
        if t.transaction_type == TransactionType.CREDIT:
            monthly_data[month_key]["income"] += float(t.amount)
        else:
            monthly_data[month_key]["expenses"] += float(t.amount)
            cat = t.category.value if t.category else "other"
            monthly_data[month_key]["by_category"][cat] = \
                monthly_data[month_key]["by_category"].get(cat, 0) + float(t.amount)
    
    # Convert to array format for frontend
    trends_array = []
    for month_key in sorted(monthly_data.keys()):
        trends_array.append(monthly_data[month_key])
    
    return trends_array


@router.get("/upcoming-payments")
async def get_upcoming_payments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get upcoming recurring payments and SIPs."""
    # Get recurring transactions
    from app.models.transaction import RecurringTransaction
    
    result = await db.execute(
        select(RecurringTransaction)
        .where(RecurringTransaction.user_id == current_user.id)
        .where(RecurringTransaction.is_active == True)
        .order_by(RecurringTransaction.next_expected_date)
    )
    recurring = result.scalars().all()
    
    # Get SIP investments
    result = await db.execute(
        select(Investment)
        .where(Investment.user_id == current_user.id)
        .where(Investment.is_sip == True)
        .where(Investment.status == InvestmentStatus.ACTIVE)
    )
    sips = result.scalars().all()
    
    upcoming = []
    
    for r in recurring:
        if r.next_expected_date:
            upcoming.append({
                "name": r.name,
                "amount": r.amount,
                "date": r.next_expected_date,
                "type": "recurring",
                "category": r.category.value
            })
    
    for s in sips:
        if s.sip_date:
            # Calculate next SIP date
            today = datetime.utcnow()
            next_date = today.replace(day=s.sip_date)
            if next_date < today:
                if today.month == 12:
                    next_date = next_date.replace(year=today.year + 1, month=1)
                else:
                    next_date = next_date.replace(month=today.month + 1)
            
            upcoming.append({
                "name": f"SIP - {s.name}",
                "amount": s.sip_amount,
                "date": next_date,
                "type": "sip",
                "category": "investments"
            })
    
    # Sort by date
    upcoming.sort(key=lambda x: x["date"])
    
    return {"upcoming_payments": upcoming[:10]}


@router.get("/goals-progress")
async def get_goals_progress(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get progress towards financial goals."""
    goals = current_user.financial_goals or {}
    
    # Get total investments
    result = await db.execute(
        select(func.sum(Investment.current_value))
        .where(Investment.user_id == current_user.id)
        .where(Investment.status == InvestmentStatus.ACTIVE)
    )
    total_investments = result.scalar() or 0
    
    # Get monthly income
    monthly_income = current_user.monthly_income or 0
    
    progress = []
    for goal_name, goal_data in goals.items():
        target = goal_data.get("target", 0)
        current = goal_data.get("current", 0)
        
        if target > 0:
            progress.append({
                "name": goal_name,
                "target": target,
                "current": current,
                "percentage": (current / target * 100),
                "deadline": goal_data.get("deadline")
            })
    
    return {
        "goals": progress,
        "total_investments": total_investments,
        "monthly_income": monthly_income
    }


@router.get("/alerts")
async def get_financial_alerts(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get financial alerts and notifications."""
    alerts = []
    
    # Check spending vs previous month
    today = datetime.utcnow()
    first_of_month = today.replace(day=1)
    
    # Get this month's spending
    result = await db.execute(
        select(func.sum(Transaction.amount))
        .where(Transaction.user_id == current_user.id)
        .where(Transaction.transaction_date >= first_of_month)
        .where(Transaction.transaction_type == TransactionType.DEBIT)
    )
    current_spending = result.scalar() or 0
    
    # Check if overspending
    monthly_income = current_user.monthly_income or 0
    if monthly_income > 0:
        days_passed = today.day
        days_in_month = 30
        expected_spending = (monthly_income * 0.7) * (days_passed / days_in_month)
        
        if current_spending > expected_spending * 1.2:
            alerts.append({
                "type": "warning",
                "title": "High Spending Alert",
                "message": f"Your spending is 20% higher than expected for this time of month.",
                "action": "Review your recent transactions"
            })
    
    # Check for upcoming bills
    from app.models.transaction import RecurringTransaction
    
    result = await db.execute(
        select(RecurringTransaction)
        .where(RecurringTransaction.user_id == current_user.id)
        .where(RecurringTransaction.is_active == True)
        .where(RecurringTransaction.next_expected_date <= today + timedelta(days=7))
    )
    upcoming_bills = result.scalars().all()
    
    for bill in upcoming_bills:
        alerts.append({
            "type": "info",
            "title": f"Upcoming: {bill.name}",
            "message": f"₹{bill.amount:,.2f} due on {bill.next_expected_date.strftime('%d %b')}",
            "action": "View details"
        })
    
    return {"alerts": alerts}
