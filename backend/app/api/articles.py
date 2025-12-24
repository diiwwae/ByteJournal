from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_current_user
from app.db import get_db

router = APIRouter()


class ArticleCreate(BaseModel):
    title: str
    body: str


class ArticleResponse(BaseModel):
    status: str


@router.post("/", response_model=ArticleResponse)
async def create_article(
    article_in: ArticleCreate,
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    # Создаем статью - триггер автоматически залогирует операцию
    q = text("""
        INSERT INTO articles (author_id, title, body)
        SELECT id, :t, :b FROM users WHERE username=:u
    """)
    try:
        await db.execute(q, {"t": article_in.title, "b": article_in.body, "u": user})
        await db.commit()
        return ArticleResponse(status="created")
    except IntegrityError as e:
        await db.rollback()

        # Проверяем, что ошибка вызвана именно нашим ограничением
        if "articles_title_length_check" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Заголовок слишком короткий (минимум 3 символа без учета пробелов)",
            )
        elif "articles_body_not_empty_check" in str(e.orig):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Содержание статьи не может быть пустым",
            )

        # Обработка других ошибок целостности
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании статьи",
        )
