"""
Cash reconciliation and quick-add endpoints
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, CurrentUser
from app.models.notification import Notification
from app.models.transaction import Transaction, TransactionType, TransactionCategory, TransactionSource
from app.services.cash_reconciliation_service import cash_reconciliation_service

router = APIRouter(prefix="/cash-check", tags=["Cash Check"])


class CashCheckResponse(BaseModel):
    """Response with cash position and suggestions."""
    user_id: str
    lookback_days: int
    last_withdrawal_date: Optional[str]
    days_since_withdrawal: Optional[int]
    total_withdrawn: float
    tracked_cash_spend: float
    estimated_untracked_cash: float
    eligible_for_nudge: bool
    suggestions: List[dict]


class QuickAddExpenseRequest(BaseModel):
    """Quick add cash expense."""
    amount: float
    subcategory: str
    description: Optional[str] = None
    transaction_date: Optional[datetime] = None


class UpdateCashPositionRequest(BaseModel):
    """Update user's estimated cash position."""
    amount_still_in_wallet: float
    note: Optional[str] = None


@router.get("/summary", response_model=CashCheckResponse)
async def get_cash_check_summary(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Get cash reconciliation summary with AI-powered suggestions.
    
    This computes:
    - Total ATM withdrawals vs tracked cash expenses
    - Estimated untracked cash still in wallet
    - Probabilistic suggestions for quick expense entry
    """
    
    # Compute cash position
    position = await cash_reconciliation_service.compute_cash_position(
        db=db,
        user_id=current_user.id,
        lookback_days=30,
        min_days_since_withdrawal=3,
    )
    
    # Generate suggestions
    suggestions_objs = await cash_reconciliation_service.suggest_likely_cash_expenses(
        db=db,
        user_id=current_user.id,
        history_days=90,
        limit=4,
    )
    
    suggestions = [
        {
            "label": s.label,
            "subcategory": s.subcategory,
            "typical_amount": s.typical_amount,
            "amount_range": {"low": s.amount_range[0], "high": s.amount_range[1]},
            "probability": round(s.probability, 2),
        }
        for s in suggestions_objs
    ]
    
    return CashCheckResponse(
        **position,
        suggestions=suggestions,
    )


@router.post("/quick-add")
async def quick_add_cash_expense(
    request: QuickAddExpenseRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    Quick-add a cash expense from the nudge dialog.
    
    Automatically tags it as cash spend for future reconciliation.
    """
    
    # Intelligently categorize based on subcategory
    subcategory_lower = request.subcategory.lower()
    if subcategory_lower in ['groceries', 'food', 'dining', 'restaurant', 'cafe']:
        category = TransactionCategory.ESSENTIALS
    elif subcategory_lower in ['transport', 'fuel', 'parking', 'taxi', 'uber']:
        category = TransactionCategory.NEEDS
    elif subcategory_lower in ['shopping', 'clothing', 'entertainment', 'movie', 'games']:
        category = TransactionCategory.SPENDS
    elif subcategory_lower in ['bills', 'utilities', 'rent', 'electricity', 'water']:
        category = TransactionCategory.BILLS
    else:
        category = TransactionCategory.OTHER
    
    transaction = Transaction(
        user_id=current_user.id,
        amount=request.amount,
        transaction_type=TransactionType.DEBIT,
        category=category,
        subcategory=request.subcategory,
        description=request.description or f"Cash - {request.subcategory}",
        source=TransactionSource.MANUAL,
        tags=["cash", "cash_spend"],
        transaction_date=request.transaction_date or datetime.utcnow(),
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return {
        "success": True,
        "transaction_id": transaction.id,
        "message": f"Added cash expense: ₹{request.amount:.2f} for {request.subcategory}",
    }


@router.post("/still-have-cash")
async def update_cash_still_in_wallet(
    request: UpdateCashPositionRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """
    User confirms they still have cash in wallet (skip nudge).
    
    We can log this as a note in user preferences for future refinement.
    """
    
    # Optional: store this as a preference or feedback log
    # For now, just acknowledge
    
    return {
        "success": True,
        "message": f"Noted: You still have ₹{request.amount_still_in_wallet:.2f} in your wallet.",
    }


@router.get("/notifications")
async def get_cash_check_notifications(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    unread_only: bool = True,
):
    """Get cash-check related notifications."""
    from sqlalchemy import select
    
    query = select(Notification).where(Notification.user_id == current_user.id)
    
    if unread_only:
        query = query.where(Notification.is_read == False)
    
    # Filter by cash-check type
    query = query.where(Notification.type.in_(["cash_check", "info"]))
    query = query.order_by(Notification.created_at.desc()).limit(20)
    
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    return {"notifications": notifications}


@router.post("/notifications/{notification_id}/mark-read")
async def mark_notification_read(
    notification_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    """Mark a notification as read."""
    from sqlalchemy import select
    
    result = await db.execute(
        select(Notification)
        .where(Notification.id == notification_id)
        .where(Notification.user_id == current_user.id)
    )
    notification = result.scalar_one_or_none()
    
    if not notification:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found",
        )
    
    notification.is_read = True
    notification.read_at = datetime.utcnow()
    
    await db.commit()
    
    return {"success": True}
