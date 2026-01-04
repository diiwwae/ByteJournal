from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Security, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_current_user
from app.db import get_db

router = APIRouter()

security_optional = HTTPBearer(auto_error=False)


class ArticleCreate(BaseModel):
    title: str
    body: str


class ArticleResponse(BaseModel):
    id: str
    author_id: str
    title: str
    created_at: datetime


class ArticleStatsResponse(BaseModel):
    article_id: str
    likes_count: int
    comments_count: int
    is_liked: bool


class LikeResponse(BaseModel):
    status: str
    is_liked: bool


class ArticleListItem(BaseModel):
    id: str
    title: str
    author_id: str
    author_username: str
    created_at: datetime
    body: str


class ArticleListResponse(BaseModel):
    articles: List[ArticleListItem]


@router.get("/", response_model=ArticleListResponse)
async def list_articles(
    db: Annotated[AsyncSession, Depends(get_db)],
    limit: Optional[int] = 50,
    offset: Optional[int] = 0,
):
    """Получить список статей из представления v_recent_articles."""
    query = text("""
        SELECT 
            article_id,
            title,
            body,
            created_at,
            author_id,
            author_username
        FROM v_recent_articles
        ORDER BY created_at DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await db.execute(query, {"limit": limit, "offset": offset})
    rows = result.fetchall()

    articles = [
        ArticleListItem(
            id=str(row.article_id),
            title=row.title,
            author_id=str(row.author_id),
            author_username=row.author_username,
            created_at=row.created_at,
            body=row.body,
        )
        for row in rows
    ]

    return ArticleListResponse(articles=articles)


@router.get("/{article_id}", response_model=ArticleListItem)
async def get_article(
    article_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить статью по ID."""
    query = text("""
        SELECT 
            article_id,
            title,
            body,
            created_at,
            author_id,
            author_username
        FROM v_recent_articles
        WHERE article_id = :article_id
    """)
    result = await db.execute(query, {"article_id": article_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена",
        )

    return ArticleListItem(
        id=str(row.article_id),
        title=row.title,
        author_id=str(row.author_id),
        author_username=row.author_username,
        created_at=row.created_at,
        body=row.body,
    )


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
        RETURNING id, author_id, title, created_at
    """)
    try:
        result = await db.execute(
            q, {"t": article_in.title, "b": article_in.body, "u": user}
        )
        row = result.fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь не найден или ошибка при создании статьи",
            )
        await db.commit()
        return ArticleResponse(
            id=str(row.id),
            author_id=str(row.author_id),
            title=row.title,
            created_at=row.created_at,
        )
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


@router.post("/{article_id}/like", response_model=LikeResponse)
async def toggle_like(
    article_id: str,
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Поставить или убрать лайк со статьи."""
    user_id = await get_user_id(user, db)

    # Проверяем, что статья существует
    article_check = text("SELECT id FROM articles WHERE id = :id")
    article_result = await db.execute(article_check, {"id": article_id})
    if not article_result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена",
        )

    # Проверяем, есть ли уже лайк
    like_check = text("""
        SELECT id, is_active 
        FROM likes 
        WHERE article_id = :article_id AND user_id = :user_id
    """)
    like_result = await db.execute(
        like_check, {"article_id": article_id, "user_id": user_id}
    )
    existing_like = like_result.fetchone()

    if existing_like:
        # Переключаем состояние лайка
        new_is_active = not existing_like.is_active
        update_query = text("""
            UPDATE likes 
            SET is_active = :is_active, updated_at = now()
            WHERE id = :id
        """)
        await db.execute(
            update_query, {"id": existing_like.id, "is_active": new_is_active}
        )
        await db.commit()
        return LikeResponse(status="toggled", is_liked=new_is_active)
    else:
        # Создаем новый лайк
        insert_query = text("""
            INSERT INTO likes (article_id, user_id, is_active)
            VALUES (:article_id, :user_id, TRUE)
        """)
        try:
            await db.execute(
                insert_query, {"article_id": article_id, "user_id": user_id}
            )
            await db.commit()
            return LikeResponse(status="liked", is_liked=True)
        except IntegrityError:
            await db.rollback()
            # Если произошла ошибка уникальности, значит лайк уже существует
            # Попробуем обновить его
            update_query = text("""
                UPDATE likes 
                SET is_active = TRUE, updated_at = now()
                WHERE article_id = :article_id AND user_id = :user_id
            """)
            await db.execute(
                update_query, {"article_id": article_id, "user_id": user_id}
            )
            await db.commit()
            return LikeResponse(status="liked", is_liked=True)


@router.get("/{article_id}/stats", response_model=ArticleStatsResponse)
async def get_article_stats(
    article_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_optional),
):
    """Получить статистику по статье (количество лайков и комментариев)."""
    # Проверяем, что статья существует
    article_check = text("SELECT id FROM articles WHERE id = :id")
    article_result = await db.execute(article_check, {"id": article_id})
    if not article_result.fetchone():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Статья не найдена",
        )

    # Получаем количество лайков
    likes_query = text("""
        SELECT COUNT(*) 
        FROM likes 
        WHERE article_id = :article_id AND is_active = TRUE
    """)
    likes_result = await db.execute(likes_query, {"article_id": article_id})
    likes_count = likes_result.scalar() or 0

    # Получаем количество комментариев
    comments_query = text("""
        SELECT COUNT(*) 
        FROM comments 
        WHERE article_id = :article_id
    """)
    comments_result = await db.execute(comments_query, {"article_id": article_id})
    comments_count = comments_result.scalar() or 0

    # Проверяем, лайкнул ли текущий пользователь (если авторизован)
    is_liked = False
    if credentials:
        try:
            user = get_current_user(credentials)
            user_id = await get_user_id(user, db)
            user_like_query = text("""
                SELECT is_active 
                FROM likes 
                WHERE article_id = :article_id AND user_id = :user_id
            """)
            user_like_result = await db.execute(
                user_like_query, {"article_id": article_id, "user_id": user_id}
            )
            user_like_row = user_like_result.fetchone()
            is_liked = user_like_row[0] if user_like_row and user_like_row[0] else False
        except (HTTPException, ValueError):
            # Если токен невалидный или пользователь не найден, просто игнорируем
            pass

    return ArticleStatsResponse(
        article_id=article_id,
        likes_count=likes_count,
        comments_count=comments_count,
        is_liked=is_liked,
    )
