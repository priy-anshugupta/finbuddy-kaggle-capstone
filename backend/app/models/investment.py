"""
Investment database models
"""

from datetime import datetime
from typing import Optional, List
from enum import Enum
import uuid

from sqlalchemy import String, Float, DateTime, Text, ForeignKey, Enum as SQLEnum, JSON, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class InvestmentType(str, Enum):
    """Investment type enumeration."""
    STOCKS = "stocks"
    MUTUAL_FUNDS = "mutual_funds"
    ETF = "etf"
    SIP = "sip"
    FIXED_DEPOSIT = "fixed_deposit"
    RECURRING_DEPOSIT = "recurring_deposit"
    PPF = "ppf"
    NPS = "nps"
    BONDS = "bonds"
    GOLD = "gold"
    REAL_ESTATE = "real_estate"
    CRYPTOCURRENCY = "cryptocurrency"
    INSURANCE = "insurance"
    OTHER = "other"


class InvestmentStatus(str, Enum):
    """Investment status enumeration."""
    ACTIVE = "active"
    MATURED = "matured"
    SOLD = "sold"
    CANCELLED = "cancelled"


class Investment(Base):
    """Investment model for portfolio tracking."""
    
    __tablename__ = "investments"
    
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
    
    # Investment Details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    symbol: Mapped[Optional[str]] = mapped_column(String(50))
    investment_type: Mapped[InvestmentType] = mapped_column(
        SQLEnum(InvestmentType),
        nullable=False
    )
    
    # Financial Details
    quantity: Mapped[float] = mapped_column(Float, default=0)
    purchase_price: Mapped[float] = mapped_column(Float, nullable=False)
    current_price: Mapped[Optional[float]] = mapped_column(Float)
    invested_amount: Mapped[float] = mapped_column(Float, nullable=False)
    current_value: Mapped[Optional[float]] = mapped_column(Float)
    
    # Returns
    absolute_return: Mapped[Optional[float]] = mapped_column(Float)
    percentage_return: Mapped[Optional[float]] = mapped_column(Float)
    xirr: Mapped[Optional[float]] = mapped_column(Float)
    
    # For SIP/Recurring
    is_sip: Mapped[bool] = mapped_column(default=False)
    sip_amount: Mapped[Optional[float]] = mapped_column(Float)
    sip_frequency: Mapped[Optional[str]] = mapped_column(String(50))
    sip_date: Mapped[Optional[int]] = mapped_column(Integer)  # Day of month
    
    # Maturity Details
    maturity_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=False))
    interest_rate: Mapped[Optional[float]] = mapped_column(Float)
    
    # Status
    status: Mapped[InvestmentStatus] = mapped_column(
        SQLEnum(InvestmentStatus),
        default=InvestmentStatus.ACTIVE
    )
    
    # Additional Data
    notes: Mapped[Optional[str]] = mapped_column(Text)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)
    
    # Timestamps
    purchase_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=False),
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="investments")
    holdings: Mapped[List["InvestmentHolding"]] = relationship(
        "InvestmentHolding",
        back_populates="investment",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Investment(id={self.id}, name={self.name}, type={self.investment_type})>"


class InvestmentHolding(Base):
    """Track individual holdings/transactions within an investment."""
    
    __tablename__ = "investment_holdings"
    
    id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    investment_id: Mapped[str] = mapped_column(
        UUID(as_uuid=False),
        ForeignKey("investments.id", ondelete="CASCADE"),
        index=True
    )
    
    # Holding Details
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Type
    holding_type: Mapped[str] = mapped_column(String(20))  # buy, sell, dividend
    
    # Timestamp
    transaction_date: Mapped[datetime] = mapped_column(DateTime(timezone=False), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    
    # Relationships
    investment: Mapped["Investment"] = relationship("Investment", back_populates="holdings")
    
    def __repr__(self) -> str:
        return f"<InvestmentHolding(id={self.id}, quantity={self.quantity})>"


class Watchlist(Base):
    """User's investment watchlist."""
    
    __tablename__ = "watchlists"
    
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
    
    # Watchlist Item
    symbol: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(255))
    investment_type: Mapped[InvestmentType] = mapped_column(SQLEnum(InvestmentType))
    
    # Alert Settings
    target_price: Mapped[Optional[float]] = mapped_column(Float)
    alert_enabled: Mapped[bool] = mapped_column(default=False)
    
    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=False), default=datetime.utcnow)
    
    def __repr__(self) -> str:
        return f"<Watchlist(id={self.id}, symbol={self.symbol})>"
