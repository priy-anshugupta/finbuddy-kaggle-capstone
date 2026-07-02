"""
Transaction API endpoints
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, CurrentUser
from app.models.transaction import Transaction, RecurringTransaction, TransactionType, TransactionCategory
from app.schemas.transaction import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
    TransactionList,
    TransactionFilter,
    TransactionStats,
    RecurringTransactionResponse,
    BulkTransactionUpload,
    OCRUploadResponse
)


router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=TransactionList)
async def get_transactions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    category: Optional[TransactionCategory] = None,
    transaction_type: Optional[TransactionType] = None,
):
    """Get paginated list of transactions with optional filters."""
    # Build query
    query = select(Transaction).where(Transaction.user_id == current_user.id)
    
    # Apply filters
    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)
    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)
    if category:
        query = query.where(Transaction.category == category)
    if transaction_type:
        query = query.where(Transaction.transaction_type == transaction_type)
    
    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()
    
    # Apply pagination
    query = query.order_by(Transaction.transaction_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return TransactionList(
        items=transactions,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=(total + page_size - 1) // page_size
    )


@router.post("", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction_data: TransactionCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Create a new transaction."""
    transaction = Transaction(
        user_id=current_user.id,
        **transaction_data.model_dump()
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.get("/stats", response_model=TransactionStats)
async def get_transaction_stats(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    """Get transaction statistics."""
    # Base query
    base_query = select(Transaction).where(Transaction.user_id == current_user.id)
    
    if start_date:
        base_query = base_query.where(Transaction.transaction_date >= start_date)
    if end_date:
        base_query = base_query.where(Transaction.transaction_date <= end_date)
    
    result = await db.execute(base_query)
    transactions = result.scalars().all()
    
    # Calculate stats
    total_income = sum(t.amount for t in transactions if t.transaction_type == TransactionType.CREDIT)
    total_expenses = sum(t.amount for t in transactions if t.transaction_type == TransactionType.DEBIT)
    
    # By category
    by_category = {}
    for t in transactions:
        if t.transaction_type == TransactionType.DEBIT:
            cat = t.category.value
            by_category[cat] = by_category.get(cat, 0) + t.amount
    
    # Top merchants
    merchant_spending = {}
    for t in transactions:
        if t.merchant_name and t.transaction_type == TransactionType.DEBIT:
            merchant_spending[t.merchant_name] = merchant_spending.get(t.merchant_name, 0) + t.amount
    
    top_merchants = [
        {"name": k, "amount": v}
        for k, v in sorted(merchant_spending.items(), key=lambda x: x[1], reverse=True)[:10]
    ]
    
    return TransactionStats(
        total_income=total_income,
        total_expenses=total_expenses,
        net_savings=total_income - total_expenses,
        by_category=by_category,
        by_month=[],  # TODO: Implement monthly breakdown
        top_merchants=top_merchants
    )


@router.get("/recurring", response_model=List[RecurringTransactionResponse])
async def get_recurring_transactions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get recurring transactions/patterns."""
    result = await db.execute(
        select(RecurringTransaction)
        .where(RecurringTransaction.user_id == current_user.id)
        .where(RecurringTransaction.is_active == True)
    )
    return result.scalars().all()


@router.get("/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific transaction."""
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .where(Transaction.user_id == current_user.id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    return transaction


@router.put("/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    transaction_update: TransactionUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Update a transaction."""
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .where(Transaction.user_id == current_user.id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    for field, value in transaction_update.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)
    
    await db.commit()
    await db.refresh(transaction)
    
    return transaction


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Delete a transaction."""
    result = await db.execute(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .where(Transaction.user_id == current_user.id)
    )
    transaction = result.scalar_one_or_none()
    
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found"
        )
    
    await db.delete(transaction)
    await db.commit()


@router.post("/bulk", response_model=List[TransactionResponse])
async def bulk_create_transactions(
    bulk_data: BulkTransactionUpload,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Create multiple transactions at once."""
    transactions = []
    for t_data in bulk_data.transactions:
        transaction = Transaction(
            user_id=current_user.id,
            **t_data.model_dump()
        )
        db.add(transaction)
        transactions.append(transaction)
    
    await db.commit()
    
    for t in transactions:
        await db.refresh(t)
    
    return transactions


@router.post("/upload/ocr", response_model=OCRUploadResponse)
async def upload_for_ocr(
    current_user: CurrentUser,
    file: UploadFile = File(...)
):
    """Upload image/PDF for OCR extraction."""
    # TODO: Implement OCR processing with agent
    # This will be handled by the OCR Agent in Orchestrator 1
    
    return OCRUploadResponse(
        extracted_transactions=[],
        confidence_scores=[],
        raw_text="OCR processing not yet implemented"
    )
