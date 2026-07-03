"""
Investment API endpoints
"""

from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, CurrentUser
from app.models.investment import Investment, InvestmentHolding, Watchlist, InvestmentType, InvestmentStatus
from app.schemas.investment import (
    InvestmentCreate,
    InvestmentUpdate,
    InvestmentResponse,
    InvestmentList,
    InvestmentHoldingCreate,
    InvestmentHoldingResponse,
    PortfolioSummary,
    WatchlistCreate,
    WatchlistResponse
)


router = APIRouter(prefix="/investments", tags=["Investments"])


@router.get("", response_model=InvestmentList)
async def get_investments(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
    investment_type: Optional[InvestmentType] = None,
    status: Optional[InvestmentStatus] = None
):
    """Get all investments for the current user."""
    query = select(Investment).where(Investment.user_id == current_user.id)
    
    if investment_type:
        query = query.where(Investment.investment_type == investment_type)
    if status:
        query = query.where(Investment.status == status)
    
    result = await db.execute(query.order_by(Investment.created_at.desc()))
    investments = result.scalars().all()
    
    # Calculate totals
    total_invested = sum(i.invested_amount for i in investments)
    total_current = sum(i.current_value or i.invested_amount for i in investments)
    total_returns = total_current - total_invested
    percentage_returns = (total_returns / total_invested * 100) if total_invested > 0 else 0
    
    return InvestmentList(
        items=investments,
        total=len(investments),
        total_invested=total_invested,
        total_current_value=total_current,
        total_returns=total_returns,
        percentage_returns=percentage_returns
    )


@router.post("", response_model=InvestmentResponse, status_code=status.HTTP_201_CREATED)
async def create_investment(
    investment_data: InvestmentCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Create a new investment."""
    # Calculate purchase price if not provided
    purchase_price = investment_data.purchase_price
    if not purchase_price and investment_data.quantity:
        purchase_price = investment_data.invested_amount / investment_data.quantity
    elif not purchase_price:
        purchase_price = investment_data.invested_amount
    
    investment = Investment(
        user_id=current_user.id,
        purchase_price=purchase_price,
        current_value=investment_data.invested_amount,
        **investment_data.model_dump(exclude={"purchase_price"})
    )
    
    db.add(investment)
    await db.commit()
    await db.refresh(investment)
    
    return investment


@router.get("/portfolio", response_model=PortfolioSummary)
async def get_portfolio_summary(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get portfolio summary and analysis."""
    result = await db.execute(
        select(Investment)
        .where(Investment.user_id == current_user.id)
        .where(Investment.status == InvestmentStatus.ACTIVE)
    )
    investments = result.scalars().all()
    
    total_invested = sum(i.invested_amount for i in investments)
    current_value = sum(i.current_value or i.invested_amount for i in investments)
    total_returns = current_value - total_invested
    percentage_returns = (total_returns / total_invested * 100) if total_invested > 0 else 0
    
    # Group by type
    by_type = {}
    for inv in investments:
        inv_type = inv.investment_type.value
        if inv_type not in by_type:
            by_type[inv_type] = {"invested": 0, "current": 0, "returns": 0}
        by_type[inv_type]["invested"] += inv.invested_amount
        by_type[inv_type]["current"] += inv.current_value or inv.invested_amount
        by_type[inv_type]["returns"] = by_type[inv_type]["current"] - by_type[inv_type]["invested"]
    
    # Group by status
    by_status = {}
    for inv in investments:
        status = inv.status.value
        by_status[status] = by_status.get(status, 0) + 1
    
    # Top and worst performers
    performers = sorted(investments, key=lambda x: x.percentage_return or 0, reverse=True)
    top_performers = [
        {"name": p.name, "returns": p.percentage_return or 0}
        for p in performers[:5] if p.percentage_return and p.percentage_return > 0
    ]
    worst_performers = [
        {"name": p.name, "returns": p.percentage_return or 0}
        for p in performers[-5:] if p.percentage_return and p.percentage_return < 0
    ]
    
    return PortfolioSummary(
        total_invested=total_invested,
        current_value=current_value,
        total_returns=total_returns,
        percentage_returns=percentage_returns,
        xirr=None,  # TODO: Calculate XIRR
        by_type=by_type,
        by_status=by_status,
        top_performers=top_performers,
        worst_performers=worst_performers
    )


@router.get("/watchlist", response_model=List[WatchlistResponse])
async def get_watchlist(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get user's watchlist."""
    result = await db.execute(
        select(Watchlist).where(Watchlist.user_id == current_user.id)
    )
    return result.scalars().all()


@router.post("/watchlist", response_model=WatchlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_watchlist(
    watchlist_data: WatchlistCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Add item to watchlist."""
    watchlist_item = Watchlist(
        user_id=current_user.id,
        **watchlist_data.model_dump()
    )
    
    db.add(watchlist_item)
    await db.commit()
    await db.refresh(watchlist_item)
    
    return watchlist_item


@router.delete("/watchlist/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_watchlist(
    item_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Remove item from watchlist."""
    result = await db.execute(
        select(Watchlist)
        .where(Watchlist.id == item_id)
        .where(Watchlist.user_id == current_user.id)
    )
    item = result.scalar_one_or_none()
    
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Watchlist item not found"
        )
    
    await db.delete(item)
    await db.commit()


@router.get("/{investment_id}", response_model=InvestmentResponse)
async def get_investment(
    investment_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Get a specific investment."""
    result = await db.execute(
        select(Investment)
        .where(Investment.id == investment_id)
        .where(Investment.user_id == current_user.id)
    )
    investment = result.scalar_one_or_none()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    return investment


@router.put("/{investment_id}", response_model=InvestmentResponse)
async def update_investment(
    investment_id: str,
    investment_update: InvestmentUpdate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Update an investment."""
    result = await db.execute(
        select(Investment)
        .where(Investment.id == investment_id)
        .where(Investment.user_id == current_user.id)
    )
    investment = result.scalar_one_or_none()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    for field, value in investment_update.model_dump(exclude_unset=True).items():
        setattr(investment, field, value)
    
    # Recalculate returns
    if investment.current_value and investment.invested_amount:
        investment.absolute_return = investment.current_value - investment.invested_amount
        investment.percentage_return = (investment.absolute_return / investment.invested_amount) * 100
    
    await db.commit()
    await db.refresh(investment)
    
    return investment


@router.delete("/{investment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_investment(
    investment_id: str,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Delete an investment."""
    result = await db.execute(
        select(Investment)
        .where(Investment.id == investment_id)
        .where(Investment.user_id == current_user.id)
    )
    investment = result.scalar_one_or_none()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    await db.delete(investment)
    await db.commit()


@router.post("/{investment_id}/holdings", response_model=InvestmentHoldingResponse)
async def add_holding(
    investment_id: str,
    holding_data: InvestmentHoldingCreate,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db)
):
    """Add a holding to an investment."""
    result = await db.execute(
        select(Investment)
        .where(Investment.id == investment_id)
        .where(Investment.user_id == current_user.id)
    )
    investment = result.scalar_one_or_none()
    
    if not investment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Investment not found"
        )
    
    holding = InvestmentHolding(
        investment_id=investment_id,
        amount=holding_data.quantity * holding_data.price,
        **holding_data.model_dump()
    )
    
    db.add(holding)
    
    # Update investment totals
    if holding_data.holding_type == "buy":
        investment.quantity = (investment.quantity or 0) + holding_data.quantity
        investment.invested_amount += holding.amount
    elif holding_data.holding_type == "sell":
        investment.quantity = (investment.quantity or 0) - holding_data.quantity
    
    await db.commit()
    await db.refresh(holding)
    
    return holding
