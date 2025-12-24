import os
from typing import Annotated

from app.db import get_db
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
security = HTTPBearer()

SECRET = os.getenv("JWT_SECRET")


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
):
    try:
        payload = jwt.decode(
            credentials.credentials, SECRET or "", algorithms=["HS256"]
        )
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
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    q = text("""
        INSERT INTO articles (author_id, title, body)
        SELECT id, :t, :b FROM users WHERE username=:u
    """)
    await db.execute(q, {"t": article_in.title, "b": article_in.body, "u": user})
    await db.commit()
    return ArticleResponse(status="created")
