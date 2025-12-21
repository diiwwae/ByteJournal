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

class ArticleResponse(BaseModel):
    status: str

@router.post("/")
async def create_article(
    article_in: ArticleCreate,
    user: str = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    q = text("""
        INSERT INTO articles (author_id, title, body)
        SELECT id, :t, :b FROM users WHERE username=:u
    """)
    await db.execute(q, {"t": article_in.title, "b": article_in.body, "u": user})
    await db.commit()
    return ArticleResponse(status="created")
