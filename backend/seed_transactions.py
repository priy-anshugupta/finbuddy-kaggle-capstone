"""
Seed script to create sample transactions in the database
Run this after a user has registered to populate their account with demo data
"""

import asyncio
import sys
from pathlib import Path

# Add the backend directory to path
sys.path.insert(0, str(Path(__file__).parent))

from datetime import datetime, timedelta
from decimal import Decimal
import random

from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.user import User
from app.models.transaction import Transaction, TransactionType, TransactionCategory


async def seed_transactions():
    """Seed sample transactions for the first user in the database."""
    
    async with async_session_maker() as session:
        # Get the first user
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ No users found. Please register a user first.")
            return
        
        print(f"✅ Found user: {user.email}")
        
        # Check if user already has transactions
        tx_result = await session.execute(
            select(Transaction).where(Transaction.user_id == user.id).limit(1)
        )
        if tx_result.scalar_one_or_none():
            print("ℹ️  User already has transactions. Skipping seed.")
            return
        
        # Sample transactions data
        sample_transactions = [
            # Income - Current Month
            {"amount": 75000, "type": TransactionType.CREDIT, "category": TransactionCategory.INCOME, 
             "merchant": "TechCorp India", "description": "Monthly Salary", "days_ago": 2, "subcategory": "Salary"},
            {"amount": 15000, "type": TransactionType.CREDIT, "category": TransactionCategory.INCOME, 
             "merchant": "Freelance Client", "description": "Web Development Project", "days_ago": 10, "subcategory": "Freelance"},
            {"amount": 5000, "type": TransactionType.CREDIT, "category": TransactionCategory.INCOME, 
             "merchant": "TechCorp India", "description": "Performance Bonus", "days_ago": 15, "subcategory": "Bonus"},
            
            # Housing & Utilities (NEEDS/ESSENTIALS)
            {"amount": 25000, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Property Owner", "description": "Monthly Rent", "days_ago": 1, "subcategory": "Rent"},
            {"amount": 4500, "type": TransactionType.DEBIT, "category": TransactionCategory.BILLS, 
             "merchant": "Electricity Board", "description": "Electricity Bill", "days_ago": 5, "subcategory": "Utilities"},
            {"amount": 1500, "type": TransactionType.DEBIT, "category": TransactionCategory.BILLS, 
             "merchant": "Jio Fiber", "description": "Internet Bill", "days_ago": 5, "is_recurring": True, "subcategory": "Internet"},
            {"amount": 1200, "type": TransactionType.DEBIT, "category": TransactionCategory.BILLS, 
             "merchant": "Municipal Corporation", "description": "Water Bill", "days_ago": 8, "subcategory": "Water"},
            {"amount": 800, "type": TransactionType.DEBIT, "category": TransactionCategory.BILLS, 
             "merchant": "Piped Natural Gas", "description": "Gas Bill", "days_ago": 12, "subcategory": "Gas"},
            
            # Food & Groceries (ESSENTIALS)
            {"amount": 8000, "type": TransactionType.DEBIT, "category": TransactionCategory.ESSENTIALS, 
             "merchant": "BigBasket", "description": "Monthly Groceries", "days_ago": 3, "subcategory": "Groceries"},
            {"amount": 4200, "type": TransactionType.DEBIT, "category": TransactionCategory.ESSENTIALS, 
             "merchant": "DMart", "description": "Household Items", "days_ago": 14, "subcategory": "Groceries"},
            {"amount": 2500, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Swiggy", "description": "Food Delivery", "days_ago": 1, "subcategory": "Dining"},
            {"amount": 1800, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Zomato", "description": "Restaurant Order", "days_ago": 4, "subcategory": "Dining"},
            {"amount": 1200, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Starbucks", "description": "Coffee & Snacks", "days_ago": 0, "subcategory": "Dining"},
            {"amount": 3500, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Barbeque Nation", "description": "Family Dinner", "days_ago": 9, "subcategory": "Dining"},
            
            # Transportation (NEEDS)
            {"amount": 3500, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Uber", "description": "Office Commute", "days_ago": 1, "subcategory": "Transport"},
            {"amount": 2000, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Indian Oil", "description": "Fuel", "days_ago": 4, "subcategory": "Transport"},
            {"amount": 1500, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Ola", "description": "Weekend Rides", "days_ago": 7, "subcategory": "Transport"},
            {"amount": 500, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Rapido", "description": "Quick Commute", "days_ago": 11, "subcategory": "Transport"},
            
            # Shopping & Lifestyle (SPENDS)
            {"amount": 5999, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Amazon", "description": "Electronics Purchase", "days_ago": 7, "subcategory": "Shopping"},
            {"amount": 3200, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Myntra", "description": "Clothing", "days_ago": 13, "subcategory": "Shopping"},
            {"amount": 1500, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Flipkart", "description": "Home Appliances", "days_ago": 18, "subcategory": "Shopping"},
            {"amount": 2800, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Nykaa", "description": "Beauty Products", "days_ago": 6, "subcategory": "Personal Care"},
            
            # Entertainment & Subscriptions (SPENDS)
            {"amount": 1299, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Netflix", "description": "Monthly Subscription", "days_ago": 15, "is_recurring": True, "subcategory": "Entertainment"},
            {"amount": 499, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Spotify", "description": "Music Subscription", "days_ago": 12, "is_recurring": True, "subcategory": "Entertainment"},
            {"amount": 299, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Amazon Prime", "description": "Prime Membership", "days_ago": 20, "is_recurring": True, "subcategory": "Entertainment"},
            {"amount": 1500, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "PVR Cinemas", "description": "Movie Tickets", "days_ago": 8, "subcategory": "Entertainment"},
            
            # Health & Fitness (NEEDS)
            {"amount": 3000, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Apollo Pharmacy", "description": "Medicines", "days_ago": 8, "subcategory": "Health"},
            {"amount": 2000, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Cult.fit", "description": "Gym Membership", "days_ago": 3, "is_recurring": True, "subcategory": "Fitness"},
            {"amount": 1500, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Dr. Sharma Clinic", "description": "Consultation Fee", "days_ago": 16, "subcategory": "Health"},
            
            # Investments
            {"amount": 5000, "type": TransactionType.DEBIT, "category": TransactionCategory.INVESTMENTS, 
             "merchant": "Zerodha", "description": "Mutual Fund SIP - HDFC Mid Cap", "days_ago": 1, "is_recurring": True, "subcategory": "Mutual Funds"},
            {"amount": 10000, "type": TransactionType.DEBIT, "category": TransactionCategory.INVESTMENTS, 
             "merchant": "ICICI Direct", "description": "Stock Purchase - Reliance", "days_ago": 6, "subcategory": "Stocks"},
            {"amount": 7500, "type": TransactionType.DEBIT, "category": TransactionCategory.INVESTMENTS, 
             "merchant": "Groww", "description": "Index Fund - Nifty 50", "days_ago": 11, "subcategory": "Index Funds"},
            {"amount": 3000, "type": TransactionType.DEBIT, "category": TransactionCategory.INVESTMENTS, 
             "merchant": "INDmoney", "description": "Gold ETF - SBI Gold", "days_ago": 19, "subcategory": "Gold ETF"},
            
            # Insurance & Financial Services (NEEDS)
            {"amount": 4500, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "HDFC Life", "description": "Term Insurance Premium", "days_ago": 10, "is_recurring": True, "subcategory": "Insurance"},
            {"amount": 2500, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "ICICI Lombard", "description": "Health Insurance", "days_ago": 22, "subcategory": "Insurance"},
            
            # Education & Learning (SPENDS)
            {"amount": 1999, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Udemy", "description": "Online Course", "days_ago": 17, "subcategory": "Education"},
            {"amount": 999, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Coursera", "description": "Certification Course", "days_ago": 25, "subcategory": "Education"},
            
            # Miscellaneous
            {"amount": 2000, "type": TransactionType.DEBIT, "category": TransactionCategory.OTHER, 
             "merchant": "Amazon Pay Gift Card", "description": "Gift Purchase", "days_ago": 13},
            {"amount": 500, "type": TransactionType.DEBIT, "category": TransactionCategory.OTHER, 
             "merchant": "Charity Organization", "description": "Donation", "days_ago": 21},
            
            # Previous Month Transactions for trend analysis
            {"amount": 72000, "type": TransactionType.CREDIT, "category": TransactionCategory.INCOME, 
             "merchant": "TechCorp India", "description": "Monthly Salary", "days_ago": 32, "subcategory": "Salary"},
            {"amount": 25000, "type": TransactionType.DEBIT, "category": TransactionCategory.NEEDS, 
             "merchant": "Property Owner", "description": "Monthly Rent", "days_ago": 31, "subcategory": "Rent"},
            {"amount": 4200, "type": TransactionType.DEBIT, "category": TransactionCategory.BILLS, 
             "merchant": "Electricity Board", "description": "Electricity Bill", "days_ago": 35, "subcategory": "Utilities"},
            {"amount": 7500, "type": TransactionType.DEBIT, "category": TransactionCategory.ESSENTIALS, 
             "merchant": "BigBasket", "description": "Monthly Groceries", "days_ago": 33, "subcategory": "Groceries"},
            {"amount": 3000, "type": TransactionType.DEBIT, "category": TransactionCategory.SPENDS, 
             "merchant": "Swiggy", "description": "Food Delivery", "days_ago": 38, "subcategory": "Dining"},
            {"amount": 5000, "type": TransactionType.DEBIT, "category": TransactionCategory.INVESTMENTS, 
             "merchant": "Zerodha", "description": "Mutual Fund SIP", "days_ago": 31, "is_recurring": True, "subcategory": "Mutual Funds"},
        ]
        
        # Create transactions
        for tx_data in sample_transactions:
            days_ago = tx_data.pop("days_ago")
            tx_date = datetime.now() - timedelta(days=days_ago)
            
            transaction = Transaction(
                user_id=user.id,
                amount=tx_data["amount"],
                transaction_type=tx_data["type"],
                category=tx_data["category"],
                subcategory=tx_data.get("subcategory"),
                merchant_name=tx_data.get("merchant"),
                description=tx_data.get("description"),
                transaction_date=tx_date,
                is_recurring=tx_data.get("is_recurring", False)
            )
            session.add(transaction)
        
        await session.commit()
        print(f"✅ Created {len(sample_transactions)} sample transactions for {user.email}")


if __name__ == "__main__":
    asyncio.run(seed_transactions())
