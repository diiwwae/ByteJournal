from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db import get_db
from app.security import hash_password, verify_password, create_token
from pydantic import BaseModel

class UserLogin(BaseModel):
    username: str
    password: str
    
class UserRegisterResponse(BaseModel):
    status: str

class UserLoginResponse(BaseModel):
    access_token: str

router = APIRouter()

@router.post("/register")
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
    return UserRegisterResponse(status="ok", user=user_in)

@router.post("/login", response_model=UserLoginResponse)
async def login(user_in: UserLogin, db: AsyncSession = Depends(get_db)):
    return UserLoginResponse(access_token=create_token(user_in.username))
