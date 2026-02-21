from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from backend.app.core.security import (
    verify_password, get_password_hash, create_access_token 
)
from backend.app.dependencies import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.models.database import Base

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

class UserRegister(BaseModel):
    email: str
    password: str
    org_name: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

@router.post("/register", response_model=Token)
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    # Simple placeholder logic until full repository bindings in next phases
    # 1. Check if org exists or create
    # 2. Hash password -> get_password_hash(user_in.password)
    # 3. Create user in DB
    # 4. Return token
    token = create_access_token("fake-user-id", "fake-org-id", "SUPER_ADMIN")
    return {"access_token": token, "token_type": "bearer"}

@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    # 1. Fetch user by email
    # user = ...
    # 2. verify_password(user_in.password, user.hashed_password)
    # 3. Return token
    token = create_access_token("fake-user-id", "fake-org-id", "SUPER_ADMIN")
    return {"access_token": token, "token_type": "bearer"}

@router.post("/refresh")
async def refresh_token():
    raise HTTPException(status_code=501, detail="Not implemented in phase 3 boilerplate")

@router.post("/logout")
async def logout():
    return {"message": "Success"}
