"""
Demo Data Seeder for FinBuddy
Seeds realistic Indian financial data for dashboard demo / Kaggle video.
Run: python seed_demo_data.py
"""

import asyncio
import sys
import os
import io
import uuid
from datetime import datetime, timedelta
import random

# Fix Windows console encoding for emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import select, text
from app.core.database import async_session_maker, init_db
from app.models.transaction import Transaction, TransactionType, TransactionCategory, TransactionSource, RecurringTransaction
from app.models.investment import Investment, InvestmentType, InvestmentStatus, InvestmentHolding
from app.models.user import User
from app.core.security import get_password_hash


# ─── Demo User ───────────────────────────────────────────────────────────────
DEMO_USER_EMAIL = "priyanshu@finbuddy.demo"
DEMO_USER_PASSWORD = "demo1234"
DEMO_USER_NAME = "Priyanshu"

# ─── Transactions (last 90 days) ─────────────────────────────────────────────
DEMO_TRANSACTIONS = [
    # ── INCOME ──
    {"amount": 85000,  "type": "credit", "cat": "income",      "desc": "Monthly Salary - June",      "merchant": "TechCorp India Pvt Ltd",   "days_ago": 5},
    {"amount": 85000,  "type": "credit", "cat": "income",      "desc": "Monthly Salary - May",       "merchant": "TechCorp India Pvt Ltd",   "days_ago": 35},
    {"amount": 85000,  "type": "credit", "cat": "income",      "desc": "Monthly Salary - April",     "merchant": "TechCorp India Pvt Ltd",   "days_ago": 65},
    {"amount": 12000,  "type": "credit", "cat": "income",      "desc": "Freelance UI Project",       "merchant": "Upwork",                   "days_ago": 20},
    {"amount": 5000,   "type": "credit", "cat": "income",      "desc": "Cashback & Rewards",         "merchant": "CRED",                     "days_ago": 10},

    # ── ESSENTIALS / NEEDS ──
    {"amount": 15000,  "type": "debit",  "cat": "essentials",  "desc": "House Rent - June",          "merchant": "Rent Transfer",            "days_ago": 3,  "recurring": True},
    {"amount": 15000,  "type": "debit",  "cat": "essentials",  "desc": "House Rent - May",           "merchant": "Rent Transfer",            "days_ago": 33, "recurring": True},
    {"amount": 6500,   "type": "debit",  "cat": "needs",       "desc": "Groceries - BigBasket",      "merchant": "BigBasket",                "days_ago": 2},
    {"amount": 4200,   "type": "debit",  "cat": "needs",       "desc": "Groceries - DMart",          "merchant": "DMart",                    "days_ago": 15},
    {"amount": 3800,   "type": "debit",  "cat": "needs",       "desc": "Groceries & Vegs",           "merchant": "Zepto",                    "days_ago": 28},

    # ── BILLS ──
    {"amount": 1299,   "type": "debit",  "cat": "bills",       "desc": "Jio Fiber - Internet",       "merchant": "Jio",                      "days_ago": 7,  "recurring": True},
    {"amount": 599,    "type": "debit",  "cat": "bills",       "desc": "Jio Mobile Recharge",        "merchant": "Jio",                      "days_ago": 12, "recurring": True},
    {"amount": 2400,   "type": "debit",  "cat": "bills",       "desc": "Electricity Bill",           "merchant": "BESCOM",                   "days_ago": 8},
    {"amount": 850,    "type": "debit",  "cat": "bills",       "desc": "Netflix Subscription",       "merchant": "Netflix",                  "days_ago": 4,  "recurring": True},
    {"amount": 199,    "type": "debit",  "cat": "bills",       "desc": "Spotify Premium",            "merchant": "Spotify",                  "days_ago": 6,  "recurring": True},
    {"amount": 1499,   "type": "debit",  "cat": "bills",       "desc": "Amazon Prime Annual",        "merchant": "Amazon",                   "days_ago": 45},

    # ── SPENDS (Lifestyle) ──
    {"amount": 1250,   "type": "debit",  "cat": "spends",      "desc": "Dinner at Barbeque Nation",  "merchant": "Barbeque Nation",          "days_ago": 1},
    {"amount": 450,    "type": "debit",  "cat": "spends",      "desc": "Starbucks Coffee",           "merchant": "Starbucks",                "days_ago": 3},
    {"amount": 3200,   "type": "debit",  "cat": "spends",      "desc": "Myntra - Clothes",           "merchant": "Myntra",                   "days_ago": 9},
    {"amount": 750,    "type": "debit",  "cat": "spends",      "desc": "Uber Rides",                 "merchant": "Uber",                     "days_ago": 2},
    {"amount": 980,    "type": "debit",  "cat": "spends",      "desc": "Swiggy Food Order",          "merchant": "Swiggy",                   "days_ago": 5},
    {"amount": 2100,   "type": "debit",  "cat": "spends",      "desc": "Amazon Shopping",            "merchant": "Amazon",                   "days_ago": 14},
    {"amount": 350,    "type": "debit",  "cat": "spends",      "desc": "Zomato Lunch",               "merchant": "Zomato",                   "days_ago": 7},
    {"amount": 1800,   "type": "debit",  "cat": "spends",      "desc": "Decathlon - Gym gear",       "merchant": "Decathlon",                "days_ago": 22},
    {"amount": 500,    "type": "debit",  "cat": "spends",      "desc": "Inox Movie Tickets",         "merchant": "BookMyShow",               "days_ago": 11},

    # ── SAVINGS ──
    {"amount": 10000,  "type": "debit",  "cat": "savings",     "desc": "Emergency Fund Transfer",    "merchant": "SBI Savings",              "days_ago": 4},
    {"amount": 10000,  "type": "debit",  "cat": "savings",     "desc": "Emergency Fund Transfer",    "merchant": "SBI Savings",              "days_ago": 34},

    # ── INVESTMENTS ──
    {"amount": 5000,   "type": "debit",  "cat": "investments", "desc": "SIP - Nifty 50 Index Fund",  "merchant": "Zerodha",                  "days_ago": 5,  "recurring": True},
    {"amount": 5000,   "type": "debit",  "cat": "investments", "desc": "SIP - Nifty 50 Index Fund",  "merchant": "Zerodha",                  "days_ago": 35, "recurring": True},
    {"amount": 3000,   "type": "debit",  "cat": "investments", "desc": "SIP - Midcap Fund",          "merchant": "Groww",                    "days_ago": 7,  "recurring": True},
    {"amount": 2500,   "type": "debit",  "cat": "investments", "desc": "PPF Contribution",           "merchant": "SBI PPF",                  "days_ago": 10},
    {"amount": 15000,  "type": "debit",  "cat": "investments", "desc": "Bought INFY shares",         "merchant": "Zerodha",                  "days_ago": 18},

    # ── TRANSFER ──
    {"amount": 5000,   "type": "debit",  "cat": "transfer",    "desc": "UPI to Mom",                 "merchant": "Google Pay",               "days_ago": 6},
    {"amount": 2000,   "type": "debit",  "cat": "transfer",    "desc": "UPI to Friend",              "merchant": "PhonePe",                  "days_ago": 13},
]


# ─── Investments Portfolio ────────────────────────────────────────────────────
DEMO_INVESTMENTS = [
    {
        "name": "UTI Nifty 50 Index Fund",
        "symbol": "UTI_NIFTY50",
        "type": "mutual_funds",
        "qty": 245.5, "buy_price": 120.0, "cur_price": 148.5,
        "invested": 29460, "current": 36452,
        "is_sip": True, "sip_amt": 5000, "sip_freq": "monthly", "sip_date": 5,
        "days_ago": 365,
    },
    {
        "name": "Kotak Emerging Equity Fund",
        "symbol": "KOTAK_MIDCAP",
        "type": "mutual_funds",
        "qty": 85.2, "buy_price": 88.5, "cur_price": 112.3,
        "invested": 7540, "current": 9568,
        "is_sip": True, "sip_amt": 3000, "sip_freq": "monthly", "sip_date": 7,
        "days_ago": 180,
    },
    {
        "name": "Infosys Limited",
        "symbol": "INFY.NS",
        "type": "stocks",
        "qty": 10, "buy_price": 1500, "cur_price": 1680,
        "invested": 15000, "current": 16800,
        "days_ago": 18,
    },
    {
        "name": "HDFC Bank Limited",
        "symbol": "HDFCBANK.NS",
        "type": "stocks",
        "qty": 5, "buy_price": 1620, "cur_price": 1745,
        "invested": 8100, "current": 8725,
        "days_ago": 90,
    },
    {
        "name": "Public Provident Fund",
        "symbol": "PPF",
        "type": "ppf",
        "qty": 1, "buy_price": 62500, "cur_price": 67000,
        "invested": 62500, "current": 67000,
        "interest_rate": 7.1,
        "days_ago": 730,
    },
    {
        "name": "Sovereign Gold Bond 2024",
        "symbol": "SGB2024",
        "type": "gold",
        "qty": 2, "buy_price": 5926, "cur_price": 7350,
        "invested": 11852, "current": 14700,
        "interest_rate": 2.5,
        "days_ago": 400,
    },
]


async def seed():
    """Seed the database with demo data."""
    await init_db()

    async with async_session_maker() as session:
        # Check if demo user already exists
        result = await session.execute(
            select(User).where(User.email == DEMO_USER_EMAIL)
        )
        user = result.scalar_one_or_none()

        if user:
            print(f"✅ Demo user already exists: {user.id}")
            # Clean existing demo transactions & investments
            await session.execute(
                text(f"DELETE FROM investment_holdings WHERE investment_id IN (SELECT id FROM investments WHERE user_id = '{user.id}')")
            )
            await session.execute(
                text(f"DELETE FROM investments WHERE user_id = '{user.id}'")
            )
            await session.execute(
                text(f"DELETE FROM transactions WHERE user_id = '{user.id}'")
            )
            await session.execute(
                text(f"DELETE FROM recurring_transactions WHERE user_id = '{user.id}'")
            )
            await session.commit()
            print("🧹 Cleaned old demo data.")
        else:
            user = User(
                id=str(uuid.uuid4()),
                email=DEMO_USER_EMAIL,
                full_name=DEMO_USER_NAME,
                hashed_password=get_password_hash(DEMO_USER_PASSWORD),
                monthly_income=85000.0,
                risk_tolerance="moderate",
                is_active=True,
                is_verified=True,
            )
            session.add(user)
            await session.commit()
            await session.refresh(user)
            print(f"✅ Created demo user: {user.email} / {DEMO_USER_PASSWORD}")

        user_id = user.id
        now = datetime.utcnow()

        # ── Seed Transactions ─────────────────────────────────────────────
        tx_count = 0
        for t in DEMO_TRANSACTIONS:
            tx = Transaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                amount=t["amount"],
                currency="INR",
                transaction_type=TransactionType(t["type"]),
                category=TransactionCategory(t["cat"]),
                description=t["desc"],
                merchant_name=t["merchant"],
                source=TransactionSource.MANUAL,
                is_recurring=t.get("recurring", False),
                is_investment=(t["cat"] == "investments"),
                is_verified=True,
                transaction_date=now - timedelta(days=t["days_ago"]),
                created_at=now - timedelta(days=t["days_ago"]),
            )
            session.add(tx)
            tx_count += 1

        print(f"📊 Added {tx_count} transactions")

        # ── Seed Investments ──────────────────────────────────────────────
        inv_count = 0
        for inv in DEMO_INVESTMENTS:
            abs_return = inv["current"] - inv["invested"]
            pct_return = (abs_return / inv["invested"]) * 100 if inv["invested"] else 0

            investment = Investment(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=inv["name"],
                symbol=inv["symbol"],
                investment_type=InvestmentType(inv["type"]),
                quantity=inv["qty"],
                purchase_price=inv["buy_price"],
                current_price=inv["cur_price"],
                invested_amount=inv["invested"],
                current_value=inv["current"],
                absolute_return=abs_return,
                percentage_return=round(pct_return, 2),
                is_sip=inv.get("is_sip", False),
                sip_amount=inv.get("sip_amt"),
                sip_frequency=inv.get("sip_freq"),
                sip_date=inv.get("sip_date"),
                interest_rate=inv.get("interest_rate"),
                status=InvestmentStatus.ACTIVE,
                purchase_date=now - timedelta(days=inv["days_ago"]),
                created_at=now - timedelta(days=inv["days_ago"]),
            )
            session.add(investment)
            inv_count += 1

        print(f"💰 Added {inv_count} investments")

        # ── Seed Recurring Transactions ────────────────────────────────────
        recurring = [
            {"name": "House Rent",          "amount": 15000, "cat": "essentials", "freq": "monthly"},
            {"name": "Jio Fiber",           "amount": 1299,  "cat": "bills",      "freq": "monthly"},
            {"name": "SIP - Nifty 50",      "amount": 5000,  "cat": "investments","freq": "monthly"},
            {"name": "SIP - Midcap Fund",   "amount": 3000,  "cat": "investments","freq": "monthly"},
            {"name": "Netflix",             "amount": 850,   "cat": "bills",      "freq": "monthly"},
            {"name": "Emergency Savings",   "amount": 10000, "cat": "savings",    "freq": "monthly"},
        ]
        for r in recurring:
            rt = RecurringTransaction(
                id=str(uuid.uuid4()),
                user_id=user_id,
                name=r["name"],
                amount=r["amount"],
                frequency=r["freq"],
                category=TransactionCategory(r["cat"]),
                is_investment=(r["cat"] == "investments"),
                is_active=True,
                next_expected_date=now + timedelta(days=random.randint(1, 28)),
                last_transaction_date=now - timedelta(days=random.randint(1, 5)),
            )
            session.add(rt)

        print(f"🔄 Added {len(recurring)} recurring transactions")

        # ── Update User Profile ─────────────────────────────────────────
        user.monthly_income = 85000.0
        user.financial_goals = {
            "emergency_fund": {"target": 200000, "current": 120000},
            "vacation": {"target": 50000, "current": 15000},
            "new_laptop": {"target": 100000, "current": 35000}
        }

        await session.commit()

    print("\n" + "=" * 50)
    print("🎉 DEMO DATA SEEDED SUCCESSFULLY!")
    print("=" * 50)
    print(f"\n  Login:    {DEMO_USER_EMAIL}")
    print(f"  Password: {DEMO_USER_PASSWORD}")
    print(f"\n  Dashboard: http://localhost:3000")
    print(f"  API Docs:  http://localhost:8000/docs")
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(seed())
