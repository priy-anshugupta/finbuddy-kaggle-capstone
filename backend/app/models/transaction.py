"""
Transaction database model
"""

from datetime import datetime
from typing import Optional
from enum import Enum
import uuid

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class TransactionType(str, Enum):
    """Transaction type enumeration."""
    CREDIT = "credit"
    DEBIT = "debit"


class TransactionCategory(str, Enum):
    """Transaction category enumeration."""
    NEEDS = "needs"
    ESSENTIALS = "essentials"
    SPENDS = "spends"
    BILLS = "bills"
    SAVINGS = "savings"
    INVESTMENTS = "investments"
    INCOME = "income"
    TRANSFER = "transfer"
    OTHER = "other"


class TransactionSource(str, Enum):
    """Source of transaction data."""
    MANUAL = "manual"
    SMS = "sms"
    BANK_STATEMENT = "bank_statement"
    RECEIPT = "receipt"
    BANK_API = "bank_api"


class Transaction(Base):
    """Transaction model for financial records."""
    
    __tablename__ = "transactions"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Transaction Details
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="INR")
    transaction_type: Mapped[TransactionType] = mapped_column(
        SQLEnum(TransactionType),
        nullable=False
    )
    
    # Categorization
    category: Mapped[TransactionCategory] = mapped_column(
        SQLEnum(TransactionCategory),
        default=TransactionCategory.OTHER
    )
    subcategory: Mapped[Optional[str]] = mapped_column(String(100))
    tags: Mapped[Optional[list]] = mapped_column(JSON, default=list)
    
    # Description
    description: Mapped[Optional[str]] = mapped_column(Text)
    merchant_name: Mapped[Optional[str]] = mapped_column(String(255))
    merchant_category: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Source Information
    source: Mapped[TransactionSource] = mapped_column(
        SQLEnum(TransactionSource),
        default=TransactionSource.MANUAL
    )
    source_reference: Mapped[Optional[str]] = mapped_column(String(255))
    raw_data: Mapped[Optional[dict]] = mapped_column(JSON)
    
    # Bank Details
    account_number: Mapped[Optional[str]] = mapped_column(String(50))
    bank_name: Mapped[Optional[str]] = mapped_column(String(100))
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    
    # Flags
    is_recurring: Mapped[bool] = mapped_column(default=False)
    is_investment: Mapped[bool] = mapped_column(default=False)
    is_verified: Mapped[bool] = mapped_column(default=False)
    is_duplicate: Mapped[bool] = mapped_column(default=False)
    
    # Timestamps
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    
    def __repr__(self) -> str:
        return f"<Transaction(id={self.id}, amount={self.amount}, type={self.transaction_type})>"


class RecurringTransaction(Base):
    """Recurring transaction pattern model."""
    
    __tablename__ = "recurring_transactions"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    user_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("users.id", ondelete="CASCADE"),
        index=True
    )
    
    # Pattern Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    frequency: Mapped[str] = mapped_column(String(50))  # daily, weekly, monthly, yearly
    
    # Category
    category: Mapped[TransactionCategory] = mapped_column(
        SQLEnum(TransactionCategory)
    )
    is_investment: Mapped[bool] = mapped_column(default=False)
    
    # Schedule
    next_expected_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    last_transaction_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    
    # Status
    is_active: Mapped[bool] = mapped_column(default=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    def __repr__(self) -> str:
        return f"<RecurringTransaction(id={self.id}, name={self.name})>"
