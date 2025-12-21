from pydantic import BaseModel

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.db import get_db
from app.api.utils import get_current_user

router = APIRouter()

class ArticleCreate(BaseModel):
    title: str
    body: str

class ArticleResponse(BaseModel):
    status: str

@router.post("/", response_model=ArticleResponse)
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
