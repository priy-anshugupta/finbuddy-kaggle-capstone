"""
Investment Pydantic schemas
"""

from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator

from app.models.investment import InvestmentType, InvestmentStatus


class InvestmentBase(BaseModel):
    """Base investment schema."""
    name: str
    symbol: Optional[str] = None
    investment_type: InvestmentType
    invested_amount: float = Field(..., gt=0)
    purchase_date: datetime
    
    @field_validator('purchase_date', mode='before')
    @classmethod
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive for PostgreSQL compatibility."""
        if v is None:
            return v
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class InvestmentCreate(InvestmentBase):
    """Schema for creating an investment."""
    quantity: Optional[float] = None
    purchase_price: Optional[float] = None
    is_sip: bool = False
    sip_amount: Optional[float] = None
    sip_frequency: Optional[str] = None
    sip_date: Optional[int] = Field(None, ge=1, le=31)
    maturity_date: Optional[datetime] = None
    interest_rate: Optional[float] = None
    notes: Optional[str] = None
    
    @field_validator('maturity_date', mode='before')
    @classmethod
    def ensure_naive_maturity(cls, v):
        """Ensure datetime is timezone-naive for PostgreSQL compatibility."""
        if v is None:
            return v
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class InvestmentUpdate(BaseModel):
    """Schema for updating an investment."""
    name: Optional[str] = None
    current_price: Optional[float] = None
    current_value: Optional[float] = None
    status: Optional[InvestmentStatus] = None
    sip_amount: Optional[float] = None
    sip_frequency: Optional[str] = None
    notes: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class InvestmentResponse(InvestmentBase):
    """Schema for investment response."""
    id: str
    user_id: str
    quantity: Optional[float]
    purchase_price: float
    current_price: Optional[float]
    current_value: Optional[float]
    absolute_return: Optional[float]
    percentage_return: Optional[float]
    xirr: Optional[float]
    is_sip: bool
    sip_amount: Optional[float]
    sip_frequency: Optional[str]
    sip_date: Optional[int]
    maturity_date: Optional[datetime]
    interest_rate: Optional[float]
    status: InvestmentStatus
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class InvestmentList(BaseModel):
    """Schema for investment list."""
    items: List[InvestmentResponse]
    total: int
    total_invested: float
    total_current_value: float
    total_returns: float
    percentage_returns: float


class InvestmentHoldingCreate(BaseModel):
    """Schema for adding a holding."""
    quantity: float
    price: float
    holding_type: str  # buy, sell, dividend
    transaction_date: datetime
    
    @field_validator('transaction_date', mode='before')
    @classmethod
    def ensure_naive_datetime(cls, v):
        """Ensure datetime is timezone-naive for PostgreSQL compatibility."""
        if v is None:
            return v
        if isinstance(v, datetime) and v.tzinfo is not None:
            return v.replace(tzinfo=None)
        return v


class InvestmentHoldingResponse(BaseModel):
    """Schema for holding response."""
    id: str
    quantity: float
    price: float
    amount: float
    holding_type: str
    transaction_date: datetime
    
    class Config:
        from_attributes = True


class PortfolioSummary(BaseModel):
    """Schema for portfolio summary."""
    total_invested: float
    current_value: float
    total_returns: float
    percentage_returns: float
    xirr: Optional[float]
    by_type: Dict[str, Dict[str, float]]
    by_status: Dict[str, int]
    top_performers: List[Dict[str, Any]]
    worst_performers: List[Dict[str, Any]]


class PortfolioAllocation(BaseModel):
    """Schema for portfolio allocation."""
    investment_type: InvestmentType
    amount: float
    percentage: float
    recommended_percentage: Optional[float] = None


class InvestmentRecommendation(BaseModel):
    """Schema for investment recommendation."""
    name: str
    symbol: Optional[str]
    investment_type: InvestmentType
    expected_returns: float
    risk_level: str
    recommendation_reason: str
    suggested_amount: Optional[float] = None
    time_horizon: Optional[str] = None


class WatchlistCreate(BaseModel):
    """Schema for adding to watchlist."""
    symbol: str
    name: str
    investment_type: InvestmentType
    target_price: Optional[float] = None
    alert_enabled: bool = False
    notes: Optional[str] = None


class WatchlistResponse(BaseModel):
    """Schema for watchlist response."""
    id: str
    symbol: str
    name: str
    investment_type: InvestmentType
    target_price: Optional[float]
    current_price: Optional[float] = None
    alert_enabled: bool
    notes: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True
