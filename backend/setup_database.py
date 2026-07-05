#!/usr/bin/env python3
"""
Script to initialize database and seed with sample data
Run this after setting up the database for the first time
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database import engine, async_session_maker
from app.models import Base, User
from seed_transactions import seed_transactions
from sqlalchemy.ext.asyncio import AsyncSession


async def init_database():
    """Initialize database tables."""
    print("🔧 Initializing database tables...")
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created successfully!")


async def check_or_create_user():
    """Check if user exists, if not prompt to create one."""
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(User).limit(1))
        user = result.scalar_one_or_none()
        
        if user:
            print(f"✅ Found existing user: {user.email}")
            return True
        else:
            print("❌ No users found in database.")
            print("📝 Please register a user first by:")
            print("   1. Starting the backend: uvicorn app.main:app --reload --port 8000")
            print("   2. Starting the frontend: cd frontend && npm run dev")
            print("   3. Register at: http://localhost:3000/register")
            print()
            print("💡 Or create a user programmatically:")
            create = input("Do you want to create a test user now? (y/N): ")
            
            if create.lower() == 'y':
                from app.models.user import User
                from app.core.security import get_password_hash
                
                email = input("Enter email (default: test@finbuddy.com): ") or "test@finbuddy.com"
                password = input("Enter password (default: password123): ") or "password123"
                full_name = input("Enter full name (default: Test User): ") or "Test User"
                
                user = User(
                    email=email,
                    hashed_password=get_password_hash(password),
                    full_name=full_name,
                    is_active=True
                )
                session.add(user)
                await session.commit()
                print(f"✅ Created user: {email}")
                return True
            else:
                return False


async def main():
    """Main setup function."""
    print("=" * 60)
    print("FinBuddy - Database Setup & Seed Script")
    print("=" * 60)
    print()
    
    try:
        # Step 1: Initialize database
        await init_database()
        print()
        
        # Step 2: Check for users
        has_user = await check_or_create_user()
        print()
        
        if has_user:
            # Step 3: Seed transactions
            print("📊 Seeding sample transactions...")
            await seed_transactions()
            print()
            print("=" * 60)
            print("✨ Database setup complete!")
            print("=" * 60)
            print()
            print("🚀 Next steps:")
            print("   1. Start backend: uvicorn app.main:app --reload --port 8000")
            print("   2. Start frontend: cd frontend && npm run dev")
            print("   3. Visit: http://localhost:3000")
            print()
        else:
            print("⏸️  Setup paused. Please create a user first.")
            print()
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
