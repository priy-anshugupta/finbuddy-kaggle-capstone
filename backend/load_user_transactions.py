"""Load 2-3 months of realistic transactions for a specific user."""

import argparse
import asyncio
import random
from datetime import datetime, timedelta

from sqlalchemy import func, select

from app.core.database import Base, async_session_maker, engine
from app.core.security import get_password_hash
from app.models.transaction import Transaction, TransactionCategory, TransactionType
from app.models.user import User


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load sample transactions for a specific user")
    parser.add_argument("--email", required=True, help="User email")
    parser.add_argument("--password", required=True, help="User password")
    parser.add_argument("--days", type=int, default=90, help="Number of days to seed")
    parser.add_argument("--seed", type=int, default=225200, help="Random seed for reproducible data")
    return parser.parse_args()


def jittered_date(days_ago: int) -> datetime:
    hours = random.randint(6, 22)
    minutes = random.randint(0, 59)
    return (datetime.utcnow() - timedelta(days=days_ago)).replace(
        hour=hours,
        minute=minutes,
        second=0,
        microsecond=0,
    )


def random_amount(min_value: int, max_value: int) -> float:
    return round(random.uniform(min_value, max_value), 2)


async def load_data(email: str, password: str, days: int, seed: int) -> None:
    random.seed(seed)

    # Ensure all tables are registered and exist
    from app.models import agent_state, conversation, investment, notification, transaction, user  # noqa: F401

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_maker() as session:
        user_result = await session.execute(select(User).where(User.email == email))
        user_obj = user_result.scalar_one_or_none()

        if user_obj is None:
            user_obj = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name="Aashutosh Mahajan",
                is_active=True,
                is_verified=True,
            )
            session.add(user_obj)
            await session.flush()
            user_status = "created"
        else:
            user_obj.hashed_password = get_password_hash(password)
            user_obj.is_active = True
            user_status = "updated"

        transactions: list[Transaction] = []

        # Monthly recurring pattern for 3 months
        month_offsets = [2, 32, 62]
        salary_amounts = [92000, 90000, 88000]
        rent_amounts = [26000, 25500, 25000]

        for index, base_day in enumerate(month_offsets):
            transactions.append(
                Transaction(
                    user_id=user_obj.id,
                    amount=float(salary_amounts[index]),
                    transaction_type=TransactionType.CREDIT,
                    category=TransactionCategory.INCOME,
                    subcategory="Salary",
                    merchant_name="TechCorp India",
                    description="Monthly Salary Credit",
                    transaction_date=jittered_date(base_day),
                )
            )
            transactions.append(
                Transaction(
                    user_id=user_obj.id,
                    amount=float(rent_amounts[index]),
                    transaction_type=TransactionType.DEBIT,
                    category=TransactionCategory.NEEDS,
                    subcategory="Rent",
                    merchant_name="Property Owner",
                    description="House Rent",
                    is_recurring=True,
                    transaction_date=jittered_date(base_day - 1 if base_day > 0 else base_day),
                )
            )
            transactions.append(
                Transaction(
                    user_id=user_obj.id,
                    amount=4499.0,
                    transaction_type=TransactionType.DEBIT,
                    category=TransactionCategory.BILLS,
                    subcategory="Utilities",
                    merchant_name="Electricity Board",
                    description="Electricity Bill",
                    is_recurring=True,
                    transaction_date=jittered_date(base_day + 2),
                )
            )
            transactions.append(
                Transaction(
                    user_id=user_obj.id,
                    amount=1499.0,
                    transaction_type=TransactionType.DEBIT,
                    category=TransactionCategory.BILLS,
                    subcategory="Internet",
                    merchant_name="Jio Fiber",
                    description="Internet Bill",
                    is_recurring=True,
                    transaction_date=jittered_date(base_day + 3),
                )
            )
            transactions.append(
                Transaction(
                    user_id=user_obj.id,
                    amount=5000.0,
                    transaction_type=TransactionType.DEBIT,
                    category=TransactionCategory.INVESTMENTS,
                    subcategory="Mutual Funds",
                    merchant_name="Zerodha",
                    description="SIP Contribution",
                    is_recurring=True,
                    transaction_date=jittered_date(base_day + 4),
                )
            )

        grocery_merchants = ["BigBasket", "DMart", "Blinkit", "Reliance Fresh"]
        dining_merchants = ["Swiggy", "Zomato", "Starbucks", "McDonald's"]
        travel_merchants = ["Uber", "Ola", "Rapido", "Indian Oil"]
        shopping_merchants = ["Amazon", "Flipkart", "Myntra", "Nykaa"]

        for day in range(days):
            if random.random() < 0.78:
                bucket = random.choices(
                    ["essentials", "spends", "needs", "bills", "invest"],
                    weights=[28, 30, 22, 10, 10],
                    k=1,
                )[0]

                if bucket == "essentials":
                    transactions.append(
                        Transaction(
                            user_id=user_obj.id,
                            amount=random_amount(350, 3200),
                            transaction_type=TransactionType.DEBIT,
                            category=TransactionCategory.ESSENTIALS,
                            subcategory="Groceries",
                            merchant_name=random.choice(grocery_merchants),
                            description="Daily/Weekly Groceries",
                            transaction_date=jittered_date(day),
                        )
                    )
                elif bucket == "spends":
                    merchant = random.choice(dining_merchants + shopping_merchants)
                    subcategory = "Dining" if merchant in dining_merchants else "Shopping"
                    transactions.append(
                        Transaction(
                            user_id=user_obj.id,
                            amount=random_amount(180, 4500),
                            transaction_type=TransactionType.DEBIT,
                            category=TransactionCategory.SPENDS,
                            subcategory=subcategory,
                            merchant_name=merchant,
                            description="Lifestyle Spend",
                            transaction_date=jittered_date(day),
                        )
                    )
                elif bucket == "needs":
                    merchant = random.choice(travel_merchants)
                    subcategory = "Transport" if merchant != "Indian Oil" else "Fuel"
                    transactions.append(
                        Transaction(
                            user_id=user_obj.id,
                            amount=random_amount(120, 2800),
                            transaction_type=TransactionType.DEBIT,
                            category=TransactionCategory.NEEDS,
                            subcategory=subcategory,
                            merchant_name=merchant,
                            description="Necessary Expense",
                            transaction_date=jittered_date(day),
                        )
                    )
                elif bucket == "bills":
                    transactions.append(
                        Transaction(
                            user_id=user_obj.id,
                            amount=random_amount(300, 2200),
                            transaction_type=TransactionType.DEBIT,
                            category=TransactionCategory.BILLS,
                            subcategory="Utility Top-up",
                            merchant_name="Mobile Recharge",
                            description="Recharge / Utility",
                            transaction_date=jittered_date(day),
                        )
                    )
                else:
                    transactions.append(
                        Transaction(
                            user_id=user_obj.id,
                            amount=random_amount(1000, 8000),
                            transaction_type=TransactionType.DEBIT,
                            category=TransactionCategory.INVESTMENTS,
                            subcategory="Stocks/ETF",
                            merchant_name="Groww",
                            description="Investment Buy",
                            transaction_date=jittered_date(day),
                        )
                    )

            if random.random() < 0.33:
                transactions.append(
                    Transaction(
                        user_id=user_obj.id,
                        amount=random_amount(80, 1600),
                        transaction_type=TransactionType.DEBIT,
                        category=TransactionCategory.SPENDS,
                        subcategory="Snacks/Coffee",
                        merchant_name=random.choice(["Cafe Coffee Day", "Starbucks", "Zomato"]),
                        description="Small Daily Spend",
                        transaction_date=jittered_date(day),
                    )
                )

        session.add_all(transactions)
        await session.commit()

        total_result = await session.execute(
            select(func.count(Transaction.id)).where(Transaction.user_id == user_obj.id)
        )
        total_count = total_result.scalar_one()

        recent_result = await session.execute(
            select(func.count(Transaction.id)).where(
                Transaction.user_id == user_obj.id,
                Transaction.transaction_date >= datetime.utcnow() - timedelta(days=days),
            )
        )
        recent_count = recent_result.scalar_one()

        print(f"USER_{user_status.upper()}: {email}")
        print(f"INSERTED_TRANSACTIONS: {len(transactions)}")
        print(f"RECENT_{days}_DAY_TRANSACTIONS: {recent_count}")
        print(f"TOTAL_TRANSACTIONS_FOR_USER: {total_count}")


def main() -> None:
    args = parse_args()
    asyncio.run(load_data(args.email, args.password, args.days, args.seed))


if __name__ == "__main__":
    main()
