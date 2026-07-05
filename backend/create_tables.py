"""
Database migration script - creates all tables
"""
import asyncio
import sys

# Windows-specific event loop fix
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

async def create_tables():
    from app.core.database import init_db
    await init_db()
    print("✅ Database tables created successfully!")

if __name__ == "__main__":
    asyncio.run(create_tables())
