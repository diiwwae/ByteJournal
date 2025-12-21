from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from app.db import get_db
from app.security import hash_password, verify_password, create_token

router = APIRouter()

@router.post("/register")
async def register(username: str, password: str, db: AsyncSession = Depends(get_db)):
    hashed = hash_password(password)
    query = text("""
        INSERT INTO users (username, password_hash)
        VALUES (:u, :p)
    """)
    try:
        await db.execute(query, {"u": username, "p": hashed})
        await db.commit()
    except Exception:
        raise HTTPException(400, "User already exists")
    return {"status": "ok"}

@router.post("/login")
async def login(username: str, password: str, db: AsyncSession = Depends(get_db)):
    query = text("SELECT password_hash FROM users WHERE username=:u")
    res = await db.execute(query, {"u": username})
    row = res.fetchone()

    if not row or not verify_password(password, row[0]):
        raise HTTPException(401, "Invalid credentials")

    token = create_token(username)
    return {"access_token": token}
