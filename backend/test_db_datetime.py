"""
Test database connection and transaction creation with datetime fix
"""
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import async_session_maker, engine
from app.models.transaction import Transaction, TransactionType, TransactionCategory, TransactionSource
from app.schemas.transaction import TransactionCreate
import uuid


async def test_db_connection():
    """Test database connection and datetime handling."""
    print("Testing database connection and datetime handling...")
    
    try:
        # Test 1: Check database connection
        async with engine.begin() as conn:
            result = await conn.execute(select(1))
            print("✅ Database connection successful")
        
        # Test 2: Create a test user ID (you should replace with actual user ID from your database)
        test_user_id = str(uuid.uuid4())
        
        # Test 3: Create transaction with timezone-naive datetime
        async with async_session_maker() as session:
            print("\nTesting transaction creation with timezone-naive datetime...")
            
            # Create a transaction
            transaction = Transaction(
                user_id=test_user_id,
                amount=100.0,
                currency="INR",
                transaction_type=TransactionType.DEBIT,
                category=TransactionCategory.ESSENTIALS,
                subcategory="test",
                tags=["test"],
                description="Test transaction for datetime fix",
                source=TransactionSource.MANUAL,
                transaction_date=datetime.utcnow(),  # Timezone-naive
                is_recurring=False,
                is_investment=False,
                is_verified=False,
                is_duplicate=False
            )
            
            session.add(transaction)
            await session.commit()
            await session.refresh(transaction)
            
            print(f"✅ Transaction created successfully!")
            print(f"   ID: {transaction.id}")
            print(f"   Transaction Date: {transaction.transaction_date}")
            print(f"   Has timezone info: {transaction.transaction_date.tzinfo is not None}")
            
            # Clean up - delete test transaction
            await session.delete(transaction)
            await session.commit()
            print("✅ Test transaction cleaned up")
        
        print("\n🎉 All database tests passed! Datetime fix is working correctly.")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    asyncio.run(test_db_connection())
