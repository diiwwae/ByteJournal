from typing import Annotated, List, Optional

from app.api.utils import get_current_user
from app.db import get_db
from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


class BatchArticleItem(BaseModel):
    title: str
    body: str


class BatchImportRequest(BaseModel):
    articles: List[BatchArticleItem] = Field(
        ..., min_length=1, description="Массив статей для импорта"
    )
    batch_size: Optional[int] = Field(
        None, ge=1, description="Размер батча для транзакций"
    )


class BatchImportResponse(BaseModel):
    total: int
    inserted: int


async def get_user_id(username: str, db: AsyncSession) -> Optional[str]:
    """Получить user_id по username."""
    query = text("SELECT id FROM users WHERE username=:u")
    result = await db.execute(query, {"u": username})
    row = result.fetchone()
    return str(row.id) if row else None


@router.post("/", response_model=BatchImportResponse)
async def batch_import(
    request: BatchImportRequest,
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Массовая загрузка статей в базу данных.

    Вставляет все статьи одним или несколькими запросами в зависимости от batch_size.
    """
    # Получаем user_id
    user_id = await get_user_id(user, db)
    if not user_id:
        raise ValueError(f"User {user} not found")

    total = len(request.articles)
    batch_size = request.batch_size or total
    inserted_count = 0

    # Обрабатываем статьи батчами
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_articles = request.articles[batch_start:batch_end]

        # Строим SQL запрос с множественными VALUES
        values_parts = []
        params = {}
        for i, article in enumerate(batch_articles):
            values_parts.append(f"(:author_id, :title_{i}, :body_{i})")
            params[f"title_{i}"] = article.title.strip()
            params[f"body_{i}"] = article.body.strip()

        params["author_id"] = user_id

        # Выполняем INSERT - триггер автоматически залогирует операцию
        insert_query = text(f"""
            INSERT INTO articles (author_id, title, body)
            VALUES {", ".join(values_parts)}
        """)

        # Выполняем массовую вставку
        await db.execute(insert_query, params)
        await db.commit()

        inserted_count += len(batch_articles)

    return BatchImportResponse(
        total=total,
        inserted=inserted_count,
    )
