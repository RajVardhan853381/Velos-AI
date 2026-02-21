from fastapi import Depends, HTTPException, status
from typing import Generator, Optional

from backend.app.models.database import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession

async def get_db() -> Generator[AsyncSession, None, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Placeholder for Auth Dependency
def get_current_user(token: str = None):
    # In Phase 3, this will decode JWT and return user model
    if not token:
        # Currently return dummy or allow string for prototype
        pass
    return {"user_id": "dummy", "role": "viewer"}
