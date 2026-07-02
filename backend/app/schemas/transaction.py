"""
Transaction Pydantic schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from app.models.transaction import TransactionType, TransactionCategory, TransactionSource


class TransactionBase(BaseModel):
    """Base transaction schema."""
    amount: float = Field(..., gt=0)
    transaction_type: TransactionType
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    transaction_date: datetime
    
    @field_validator('transaction_date', mode='before')
    @classmethod
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive for PostgreSQL compatibility."""
        if v is None:
            return v
        if isinstance(v, datetime) and v.tzinfo is not None:
            # Convert to UTC and remove timezone info
            return v.replace(tzinfo=None)
        return v


class TransactionCreate(TransactionBase):
    """Schema for creating a transaction."""
    category: Optional[TransactionCategory] = TransactionCategory.OTHER
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = []
    source: TransactionSource = TransactionSource.MANUAL
    account_number: Optional[str] = None
    bank_name: Optional[str] = None
    is_recurring: bool = False
    is_investment: bool = False


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""
    amount: Optional[float] = Field(None, gt=0)
    transaction_type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    description: Optional[str] = None
    merchant_name: Optional[str] = None
    is_recurring: Optional[bool] = None
    is_investment: Optional[bool] = None
    is_verified: Optional[bool] = None


class TransactionResponse(TransactionBase):
    """Schema for transaction response."""
    id: str
    user_id: str
    currency: str
    category: TransactionCategory
    subcategory: Optional[str]
    tags: Optional[List[str]]
    merchant_category: Optional[str]
    source: TransactionSource
    account_number: Optional[str]
    bank_name: Optional[str]
    is_recurring: bool
    is_investment: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class TransactionList(BaseModel):
    """Schema for paginated transaction list."""
    items: List[TransactionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class TransactionFilter(BaseModel):
    """Schema for transaction filtering."""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    category: Optional[TransactionCategory] = None
    transaction_type: Optional[TransactionType] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    merchant_name: Optional[str] = None
    is_recurring: Optional[bool] = None


class TransactionStats(BaseModel):
    """Schema for transaction statistics."""
    total_income: float
    total_expenses: float
    net_savings: float
    by_category: Dict[str, float]
    by_month: List[Dict[str, Any]]
    top_merchants: List[Dict[str, Any]]


class RecurringTransactionResponse(BaseModel):
    """Schema for recurring transaction response."""
    id: str
    name: str
    description: Optional[str]
    amount: float
    frequency: str
    category: TransactionCategory
    is_investment: bool
    next_expected_date: Optional[datetime]
    last_transaction_date: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class BulkTransactionUpload(BaseModel):
    """Schema for bulk transaction upload."""
    transactions: List[TransactionCreate]


class OCRUploadResponse(BaseModel):
    """Schema for OCR upload response."""
    extracted_transactions: List[TransactionCreate]
    confidence_scores: List[float]
    raw_text: Optional[str] = None
