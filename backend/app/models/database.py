import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, declared_attr
from datetime import datetime
from typing import Any
from backend.app.config import settings

# Dual DB Support
# If SQLite, use aiosqlite, if Postgres, use asyncpg
DATABASE_URL = settings.DATABASE_URL
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLite needs special connect args for async
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.ENVIRONMENT == "dev",
    connect_args=connect_args,
    # pool config disabled for sqlite, enabled for pg
    **( {"pool_size": 10, "max_overflow": 20} if "postgresql" in DATABASE_URL else {} )
)

# Application-wide session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autoflush=False
)

class Base(DeclarativeBase):
    """
    Base for all SQLAlchemy models.
    Provides table name generation and automatic common timestamp columns.
    """
    id: Any
    __name__: str
    
    # Generate __tablename__ automatically from class name
    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower() + "s"
