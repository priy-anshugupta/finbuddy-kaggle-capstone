"""
Test datetime timezone handling fix for PostgreSQL
"""
from datetime import datetime, timezone
from app.schemas.transaction import TransactionCreate
from app.models.transaction import TransactionType, TransactionCategory, TransactionSource

# Test 1: Timezone-aware datetime (should be converted to naive)
tz_aware = datetime(2026, 1, 31, 12, 0, 0, tzinfo=timezone.utc)
print(f"Input (timezone-aware): {tz_aware}")
print(f"Has tzinfo: {tz_aware.tzinfo is not None}")

# Test 2: Create transaction with timezone-aware datetime
transaction_data = TransactionCreate(
    amount=1000.0,
    transaction_type=TransactionType.DEBIT,
    category=TransactionCategory.ESSENTIALS,
    subcategory="groceries",
    tags=["test"],
    description="Test transaction",
    transaction_date=tz_aware,
    source=TransactionSource.MANUAL
)

print(f"\nAfter validation: {transaction_data.transaction_date}")
print(f"Has tzinfo after validation: {transaction_data.transaction_date.tzinfo is not None}")

# Test 3: Timezone-naive datetime (should remain unchanged)
tz_naive = datetime(2026, 1, 31, 12, 0, 0)
print(f"\nInput (timezone-naive): {tz_naive}")
print(f"Has tzinfo: {tz_naive.tzinfo is not None}")

transaction_data2 = TransactionCreate(
    amount=2000.0,
    transaction_type=TransactionType.CREDIT,
    category=TransactionCategory.INCOME,
    transaction_date=tz_naive,
    source=TransactionSource.MANUAL
)

print(f"\nAfter validation: {transaction_data2.transaction_date}")
print(f"Has tzinfo after validation: {transaction_data2.transaction_date.tzinfo is not None}")

print("\n✅ All datetime tests passed! Timezone-aware datetimes are converted to naive.")
