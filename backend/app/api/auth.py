from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_current_user
from app.db import get_db
from app.security import create_token, hash_password, verify_password


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
    role_id: str
    is_active: bool
    created_at: datetime


router = APIRouter()


@router.post("/register", response_model=UserRegisterResponse)
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
    # Проверяем существование пользователя в базе данных
    query = text("SELECT password_hash FROM users WHERE username=:u")
    res = await db.execute(query, {"u": user_in.username})
    row = res.mappings().fetchone()

    # Если пользователь не найден, возвращаем 401
    if not row:
        raise HTTPException(status_code=401, detail="Invalid username")

    # Проверяем правильность пароля
    if not verify_password(user_in.password, row["password_hash"]):
        raise HTTPException(status_code=401, detail="Invalid password")

    # Проверяем, что пользователь активен
    # if not row.is_active:
    #     raise HTTPException(status_code=401, detail="User account is inactive")

    # Если все проверки пройдены, создаем токен
    return UserLoginResponse(access_token=create_token(user_in.username))


@router.get("/me", response_model=UserMeResponse)
async def me(
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    query = text(
        "SELECT id, username, role_id, is_active, created_at FROM users WHERE username=:u"
    )
    res = await db.execute(query, {"u": user})
    row = res.mappings().fetchone()

    if not row:
        raise HTTPException(401, "User not found")

    return UserMeResponse(
        id=str(row["id"]),
        username=row["username"],
        is_active=row["is_active"],
        role_id=str(row["role_id"]),
        created_at=row["created_at"],
    )
