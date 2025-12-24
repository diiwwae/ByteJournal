from datetime import datetime
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_current_user
from app.db import get_db

router = APIRouter()


class CommentCreate(BaseModel):
    article_id: str = Field(..., description="ID статьи")
    content: str = Field(..., min_length=1, description="Текст комментария")


class CommentResponse(BaseModel):
    id: str
    article_id: str
    user_id: str
    username: str
    content: str
    is_edited: bool
    created_at: datetime
    updated_at: datetime


class CommentListResponse(BaseModel):
    comments: List[CommentResponse]


async def get_user_id(username: str, db: AsyncSession) -> str:
    """Получить user_id по username."""
    query = text("SELECT id FROM users WHERE username=:u")
    result = await db.execute(query, {"u": username})
    row = result.fetchone()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return str(row.id)


@router.post("/", response_model=CommentResponse)
async def create_comment(
    comment_in: CommentCreate,
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Добавить комментарий к статье."""
    user_id = await get_user_id(user, db)

    # Проверяем, что статья существует
    article_check = text("SELECT id FROM articles WHERE id = :id")
    article_result = await db.execute(article_check, {"id": comment_in.article_id})
    if not article_result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена",
        )

    # Создаем комментарий
    query = text("""
        INSERT INTO comments (article_id, user_id, content)
        VALUES (:article_id, :user_id, :content)
        RETURNING id, article_id, user_id, content, is_edited, created_at, updated_at
    """)

    try:
        result = await db.execute(
            query,
            {
                "article_id": comment_in.article_id,
                "user_id": user_id,
                "content": comment_in.content.strip(),
            },
        )
        await db.commit()
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании комментария",
            )

        # Получаем username для ответа
        username_query = text("SELECT username FROM users WHERE id = :id")
        username_result = await db.execute(username_query, {"id": user_id})
        username_row = username_result.fetchone()
        username = username_row[0] if username_row else user

        return CommentResponse(
            id=str(row.id),
            article_id=str(row.article_id),
            user_id=str(row.user_id),
            username=username,
            content=row.content,
            is_edited=row.is_edited,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig)

        if "comments_content_not_empty_check" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Содержание комментария не может быть пустым",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании комментария",
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )


@router.get("/article/{article_id}", response_model=CommentListResponse)
async def get_article_comments(
    article_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить все комментарии к статье."""
    # Проверяем, что статья существует
    article_check = text("SELECT id FROM articles WHERE id = :id")
    article_result = await db.execute(article_check, {"id": article_id})
    if not article_result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена",
        )

    query = text("""
        SELECT 
            c.id,
            c.article_id,
            c.user_id,
            u.username,
            c.content,
            c.is_edited,
            c.created_at,
            c.updated_at
        FROM comments c
        JOIN users u ON c.user_id = u.id
        WHERE c.article_id = :article_id
        ORDER BY c.created_at ASC
    """)

    result = await db.execute(query, {"article_id": article_id})
    rows = result.fetchall()

    comments = [
        CommentResponse(
            id=str(row.id),
            article_id=str(row.article_id),
            user_id=str(row.user_id),
            username=row.username,
            content=row.content,
            is_edited=row.is_edited,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]

    return CommentListResponse(comments=comments)

