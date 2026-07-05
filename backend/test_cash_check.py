"""
Quick test script for cash reconciliation feature
"""

import asyncio
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.insert(0, '.')

from app.core.database import async_session_maker
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionSource
from app.services.cash_reconciliation_service import cash_reconciliation_service


async def create_test_data(user_id: str):
    """Create test transactions for cash reconciliation."""
    async with async_session_maker() as db:
        # Create ATM withdrawal
        withdrawal = Transaction(
            user_id=user_id,
            amount=10000.0,
            transaction_type=TransactionType.DEBIT,
            description="ATM Withdrawal",
            merchant_name="HDFC ATM",
            source=TransactionSource.MANUAL,
            tags=["cash_withdrawal"],
            transaction_date=datetime.utcnow() - timedelta(days=5),
        )
        db.add(withdrawal)
        
        # Create some cash expenses
        cash_expenses = [
            Transaction(
                user_id=user_id,
                amount=500.0,
                transaction_type=TransactionType.DEBIT,
                description="Groceries - cash",
                subcategory="groceries",
                source=TransactionSource.MANUAL,
                tags=["cash", "cash_spend"],
                transaction_date=datetime.utcnow() - timedelta(days=3),
            ),
            Transaction(
                user_id=user_id,
                amount=200.0,
                transaction_type=TransactionType.DEBIT,
                description="Transport - cash",
                subcategory="transport",
                source=TransactionSource.MANUAL,
                tags=["cash", "cash_spend"],
                transaction_date=datetime.utcnow() - timedelta(days=2),
            ),
            Transaction(
                user_id=user_id,
                amount=300.0,
                transaction_type=TransactionType.DEBIT,
                description="Food - cash",
                subcategory="food",
                source=TransactionSource.MANUAL,
                tags=["cash", "cash_spend"],
                transaction_date=datetime.utcnow() - timedelta(days=1),
            ),
        ]
        
        for expense in cash_expenses:
            db.add(expense)
        
        await db.commit()
        print(f"✅ Created test data for user {user_id}")
        print(f"   - 1 ATM withdrawal: ₹10,000")
        print(f"   - 3 cash expenses: ₹1,000 total")
        print(f"   - Expected untracked: ₹9,000")


async def test_cash_check(user_id: str):
    """Test cash reconciliation service."""
    async with async_session_maker() as db:
        print("\n🔍 Testing cash reconciliation...")
        
        # Get cash position
        position = await cash_reconciliation_service.compute_cash_position(
            db=db,
            user_id=user_id,
            lookback_days=30,
            min_days_since_withdrawal=3,
        )
        
        print("\n💰 Cash Position:")
        print(f"   Total withdrawn: ₹{position['total_withdrawn']:,.2f}")
        print(f"   Tracked cash spend: ₹{position['tracked_cash_spend']:,.2f}")
        print(f"   Estimated untracked: ₹{position['estimated_untracked_cash']:,.2f}")
        print(f"   Days since withdrawal: {position['days_since_withdrawal']}")
        print(f"   Eligible for nudge: {position['eligible_for_nudge']}")
        
        # Get suggestions
        suggestions = await cash_reconciliation_service.suggest_likely_cash_expenses(
            db=db,
            user_id=user_id,
            history_days=90,
            limit=4,
        )
        
        print("\n✨ AI Suggestions:")
        for i, s in enumerate(suggestions, 1):
            print(f"   {i}. {s.label}: ₹{s.typical_amount} "
                  f"(₹{s.amount_range[0]}-₹{s.amount_range[1]}, "
                  f"{s.probability*100:.0f}% prob)")


async def main():
    """Run tests."""
    print("🧪 Cash Reconciliation Test Script")
    print("=" * 50)
    
    # Get first active user (or specify user_id)
    async with async_session_maker() as db:
        from sqlalchemy import select
        result = await db.execute(
            select(User).where(User.is_active == True).limit(1)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No active users found. Create a user first.")
            return
        
        print(f"📧 Using user: {user.email} ({user.id})")
        
        # Ask if we should create test data
        print("\n⚠️  This will create test transactions.")
        response = input("Create test data? (y/N): ").lower()
        
        if response == 'y':
            await create_test_data(user.id)
        
        # Run cash check
        await test_cash_check(user.id)
        
        print("\n" + "=" * 50)
        print("✅ Test complete!")
        print("\n💡 Next steps:")
        print("   1. Check the frontend: http://localhost:3000/dashboard")
        print("   2. View transactions page to see the widget")
        print("   3. Run nightly task manually:")
        print("      from app.services.tasks import nightly_cash_check")
        print("      nightly_cash_check()")


if __name__ == "__main__":
    asyncio.run(main())
