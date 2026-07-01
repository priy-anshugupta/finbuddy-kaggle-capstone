"""
SQLite Database Fallback for Local Development

This module provides a SQLite-based async database engine that works
as a drop-in replacement for PostgreSQL when running locally for testing.

Usage:
    In .env, set: DATABASE_URL=sqlite+aiosqlite:///./finbuddy_local.db
    Or import and use: engine = create_sqlite_engine()
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def create_sqlite_engine(database_path: str = "./finbuddy_local.db"):
    """Create an async SQLite engine for local development."""
    return create_async_engine(
        f"sqlite+aiosqlite:///{database_path}",
        echo=False,
        future=True,
    )


async_session_maker = async_sessionmaker(
    expire_on_commit=False,
    class_=AsyncSession,
)
