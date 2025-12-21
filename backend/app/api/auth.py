from datetime import datetime
from pydantic import BaseModel

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_current_user
from app.db import get_db
from app.security import create_token, hash_password


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegisterResponse(BaseModel):
    status: str


class UserLoginResponse(BaseModel):
    access_token: str


class UserMeResponse(BaseModel):
    id: str
    username: str
    is_active: bool
    created_at: datetime


router = APIRouter()


@router.post("/register", response_model=UserRegisterResponse)
async def register(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    hashed = hash_password(user_in.password)
    query = text("""
        INSERT INTO users (username, password_hash)
        VALUES (:u, :p)
    """)
    try:
        await db.execute(query, {"u": user_in.username, "p": hashed})
        await db.commit()
    except Exception:
        raise HTTPException(400, "User already exists")
    return UserRegisterResponse(status="ok")


@router.post("/login", response_model=UserLoginResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    return UserLoginResponse(access_token=create_token(user_in.username))


# @router.get("/me", response_model=UserMeResponse)
# async def me(user: str = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
#     query = text("SELECT username FROM users WHERE username=:u")
#     try:
#         res = await db.execute(query, {"u": user})
#         row = res.fetchone()
#         if not row:
#             raise HTTPException(401, "User not found")
#         return UserMeResponse(user=row[0])
#     except Exception:
#         raise HTTPException(500, "Internal server error")
