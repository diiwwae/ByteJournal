from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from jose import jwt, JWTError
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
import os
from app.db import get_db

router = APIRouter()
security = HTTPBearer()

SECRET = os.getenv("JWT_SECRET")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

class ArticleCreate(BaseModel):
    title: str
    body: str

@router.post("/")
async def create_article(
    title: str,
    body: str,
    user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    q = text("""
        INSERT INTO articles (author_id, title, body)
        SELECT id, :t, :b FROM users WHERE username=:u
    """)
    await db.execute(q, {"t": title, "b": body, "u": user})
    await db.commit()
    return {"status": "created"}
