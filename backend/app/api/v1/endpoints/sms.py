"""
SMS Transaction API endpoints for Android Connector
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field
import uuid
import hashlib

from app.dependencies import get_db, CurrentUser
from app.models.transaction import Transaction, TransactionType, TransactionCategory, TransactionSource


router = APIRouter(prefix="/sms", tags=["SMS Transactions"])


# Request/Response Models
class ParsedTransactionData(BaseModel):
    """Parsed data from SMS"""
    amount: Optional[float] = None
    transaction_type: Optional[str] = None  # "credit" or "debit"
    category: Optional[str] = None  # Category from Android app
    merchant: Optional[str] = None
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    balance: Optional[float] = None
    reference_number: Optional[str] = None
    transaction_date: Optional[str] = None


class SmsTransactionRequest(BaseModel):
    """Single SMS transaction upload request"""
    sms_body: str = Field(..., description="Original SMS message body")
    sender: str = Field(..., description="SMS sender ID")
    timestamp: int = Field(..., description="SMS timestamp in milliseconds")
    parsed_data: Optional[ParsedTransactionData] = None


class SmsTransactionResponse(BaseModel):
    """Response for single SMS transaction"""
    id: str
    status: str
    message: str


class BatchTransactionRequest(BaseModel):
    """Batch of SMS transactions"""
    transactions: List[SmsTransactionRequest]


class BatchTransactionResponse(BaseModel):
    """Response for batch SMS transaction upload"""
    total_received: int
    total_processed: int
    total_failed: int
    total_duplicates: int
    transaction_ids: List[str]


class SyncStatusResponse(BaseModel):
    """Sync status response"""
    last_sync: Optional[int] = None
    pending_count: int = 0
    total_synced: int = 0


class SyncCompleteRequest(BaseModel):
    """Sync completion notification"""
    sync_timestamp: int
    transactions_count: int


def generate_sms_hash(sms_body: str, sender: str, timestamp: int) -> str:
    """Generate unique hash for SMS to detect duplicates"""
    content = f"{sms_body}:{sender}:{timestamp}"
    return hashlib.sha256(content.encode()).hexdigest()[:32]


def parse_transaction_type(type_str: Optional[str]) -> TransactionType:
    """Convert string to TransactionType enum"""
    if type_str:
        type_lower = type_str.lower()
        if type_lower == "credit":
            return TransactionType.CREDIT
        elif type_lower == "debit":
            return TransactionType.DEBIT
    return TransactionType.DEBIT  # Default to debit if unknown


def categorize_transaction(parsed_data: Optional[ParsedTransactionData]) -> TransactionCategory:
    """Auto-categorize transaction based on parsed data"""
    if not parsed_data:
        return TransactionCategory.OTHER
    
    # Use category from Android app if provided
    if parsed_data.category:
        category_map = {
            "needs": TransactionCategory.NEEDS,
            "essentials": TransactionCategory.ESSENTIALS,
            "spends": TransactionCategory.SPENDS,
            "bills": TransactionCategory.BILLS,
            "savings": TransactionCategory.SAVINGS,
            "investments": TransactionCategory.INVESTMENTS,
            "income": TransactionCategory.INCOME,
            "transfer": TransactionCategory.TRANSFER,
            "other": TransactionCategory.OTHER,
        }
        return category_map.get(parsed_data.category.lower(), TransactionCategory.OTHER)
    
    if not parsed_data.merchant:
        return TransactionCategory.OTHER
    
    merchant_lower = parsed_data.merchant.lower()
    
    # Define category mappings
    category_keywords = {
        TransactionCategory.BILLS: ["electricity", "water", "gas", "broadband", "internet", "mobile", "phone", "recharge"],
        TransactionCategory.ESSENTIALS: ["grocery", "groceries", "supermarket", "vegetables", "milk", "provisions"],
        TransactionCategory.SPENDS: ["restaurant", "cafe", "coffee", "movie", "entertainment", "shopping", "mall"],
        TransactionCategory.INVESTMENTS: ["mutual", "fund", "stock", "share", "sip", "investment", "trading"],
        TransactionCategory.INCOME: ["salary", "credit", "refund", "cashback"],
        TransactionCategory.TRANSFER: ["transfer", "neft", "imps", "rtgs", "upi"],
        TransactionCategory.SAVINGS: ["fd", "fixed deposit", "rd", "recurring"],
    }
    
    for category, keywords in category_keywords.items():
        if any(keyword in merchant_lower for keyword in keywords):
            return category
    
    return TransactionCategory.OTHER


@router.post("/transactions", response_model=SmsTransactionResponse, status_code=status.HTTP_201_CREATED)
async def upload_sms_transaction(
    request: SmsTransactionRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Upload a single SMS transaction from the Android app"""
    
    # Generate hash to check for duplicates
    sms_hash = generate_sms_hash(request.sms_body, request.sender, request.timestamp)
    
    # Check for duplicates
    existing_query = select(Transaction).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.source_reference == sms_hash
        )
    )
    existing = (await db.execute(existing_query)).scalar_one_or_none()
    
    if existing:
        return SmsTransactionResponse(
            id=existing.id,
            status="duplicate",
            message="Transaction already exists"
        )
    
    # Parse transaction data
    parsed = request.parsed_data
    transaction_type = parse_transaction_type(parsed.transaction_type if parsed else None)
    category = categorize_transaction(parsed)
    
    # Convert timestamp to datetime
    transaction_date = datetime.fromtimestamp(request.timestamp / 1000)
    
    # Create transaction
    transaction = Transaction(
        id=str(uuid.uuid4()),
        user_id=current_user.id,
        amount=parsed.amount if parsed and parsed.amount else 0.0,
        transaction_type=transaction_type,
        category=category,
        description=request.sms_body[:500],  # Limit description length
        merchant_name=parsed.merchant if parsed else None,
        source=TransactionSource.SMS,
        source_reference=sms_hash,
        raw_data={
            "sms_body": request.sms_body,
            "sender": request.sender,
            "timestamp": request.timestamp,
            "parsed_data": parsed.dict() if parsed else None
        },
        account_number=parsed.account_number if parsed else None,
        bank_name=parsed.bank_name if parsed else request.sender,
        transaction_id=parsed.reference_number if parsed else None,
        transaction_date=transaction_date,
        is_verified=False
    )
    
    db.add(transaction)
    await db.commit()
    await db.refresh(transaction)
    
    return SmsTransactionResponse(
        id=transaction.id,
        status="created",
        message="Transaction created successfully"
    )


@router.post("/transactions/batch", response_model=BatchTransactionResponse)
async def upload_sms_transactions_batch(
    requests: List[SmsTransactionRequest],
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Upload multiple SMS transactions in batch from the Android app"""
    
    total_received = len(requests)
    total_processed = 0
    total_failed = 0
    total_duplicates = 0
    transaction_ids = []
    
    for request in requests:
        try:
            # Generate hash to check for duplicates
            sms_hash = generate_sms_hash(request.sms_body, request.sender, request.timestamp)
            
            # Check for duplicates
            existing_query = select(Transaction).where(
                and_(
                    Transaction.user_id == current_user.id,
                    Transaction.source_reference == sms_hash
                )
            )
            existing = (await db.execute(existing_query)).scalar_one_or_none()
            
            if existing:
                total_duplicates += 1
                transaction_ids.append(existing.id)
                continue
            
            # Parse transaction data
            parsed = request.parsed_data
            transaction_type = parse_transaction_type(parsed.transaction_type if parsed else None)
            category = categorize_transaction(parsed)
            
            # Convert timestamp to datetime
            transaction_date = datetime.fromtimestamp(request.timestamp / 1000)
            
            # Create transaction
            transaction = Transaction(
                id=str(uuid.uuid4()),
                user_id=current_user.id,
                amount=parsed.amount if parsed and parsed.amount else 0.0,
                transaction_type=transaction_type,
                category=category,
                description=request.sms_body[:500],
                merchant_name=parsed.merchant if parsed else None,
                source=TransactionSource.SMS,
                source_reference=sms_hash,
                raw_data={
                    "sms_body": request.sms_body,
                    "sender": request.sender,
                    "timestamp": request.timestamp,
                    "parsed_data": parsed.dict() if parsed else None
                },
                account_number=parsed.account_number if parsed else None,
                bank_name=parsed.bank_name if parsed else request.sender,
                transaction_id=parsed.reference_number if parsed else None,
                transaction_date=transaction_date,
                is_verified=False
            )
            
            db.add(transaction)
            transaction_ids.append(transaction.id)
            total_processed += 1
            
        except Exception as e:
            total_failed += 1
            continue
    
    await db.commit()
    
    return BatchTransactionResponse(
        total_received=total_received,
        total_processed=total_processed,
        total_failed=total_failed,
        total_duplicates=total_duplicates,
        transaction_ids=transaction_ids
    )


@router.get("/sync-status", response_model=SyncStatusResponse)
async def get_sync_status(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get sync status for the user's SMS transactions"""
    
    # Get last SMS transaction timestamp
    last_sync_query = select(Transaction.transaction_date).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.source == TransactionSource.SMS
        )
    ).order_by(Transaction.transaction_date.desc()).limit(1)
    
    result = (await db.execute(last_sync_query)).scalar_one_or_none()
    last_sync = int(result.timestamp() * 1000) if result else None
    
    # Get total SMS transactions count
    count_query = select(func.count()).select_from(Transaction).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.source == TransactionSource.SMS
        )
    )
    total_synced = (await db.execute(count_query)).scalar() or 0
    
    return SyncStatusResponse(
        last_sync=last_sync,
        pending_count=0,
        total_synced=total_synced
    )


@router.post("/sync-complete", status_code=status.HTTP_204_NO_CONTENT)
async def mark_sync_complete(
    request: SyncCompleteRequest,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Mark a sync operation as complete"""
    # This can be used to log sync events or update user preferences
    # For now, we just acknowledge the sync completion
    return None


@router.get("/transactions/sms", response_model=List[dict])
async def get_sms_transactions(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    limit: int = 50,
    offset: int = 0
):
    """Get SMS-sourced transactions for the current user"""
    
    query = select(Transaction).where(
        and_(
            Transaction.user_id == current_user.id,
            Transaction.source == TransactionSource.SMS
        )
    ).order_by(Transaction.transaction_date.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    transactions = result.scalars().all()
    
    return [
        {
            "id": t.id,
            "amount": t.amount,
            "transaction_type": t.transaction_type.value,
            "category": t.category.value,
            "merchant_name": t.merchant_name,
            "bank_name": t.bank_name,
            "transaction_date": t.transaction_date.isoformat(),
            "is_verified": t.is_verified
        }
        for t in transactions
    ]
