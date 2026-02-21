from typing import Optional
from fastapi import Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.database import Base

class TenantRepository:
    """
    Mixin/Base for repositories to automatically enforce tenant isolation.
    """
    def __init__(self, model: Base):
        self.model = model

    def get_tenant_id(self, request: Request) -> str:
        """Extract org_id from the authenticated user's token."""
        if not hasattr(request.state, "user") or not request.state.user.org_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate tenant credentials"
            )
        return request.state.user.org_id
