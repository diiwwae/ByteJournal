from typing import Annotated

from app.db import get_db
from app.security import create_token, hash_password
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


class UserLogin(BaseModel):
    username: str
    password: str


class UserRegisterResponse(BaseModel):
    status: str


class UserLoginResponse(BaseModel):
    access_token: str


router = APIRouter()


@router.post("/register")
async def register(user_in: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]):
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
async def login(user_in: UserLogin, db: Annotated[AsyncSession, Depends(get_db)]):
    return UserLoginResponse(access_token=create_token(user_in.username))
