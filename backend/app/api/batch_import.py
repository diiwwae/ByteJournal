from typing import Annotated, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_current_user
from app.db import get_db

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
    failed: int
    errors: List[Dict[str, str]] = Field(default_factory=list)


async def get_user_id(username: str, db: AsyncSession) -> Optional[str]:
    """Получить user_id по username."""
    query = text("SELECT id FROM users WHERE username=:u")
    result = await db.execute(query, {"u": username})
    row = result.fetchone()
    return str(row.id) if row else None


async def log_import_error(
    db: AsyncSession,
    user_id: str,
    row_number: int,
    status_text: str,
    error_message: str,
    filename: Optional[str] = None,
):
    """Логирует ошибку импорта в таблицу import_logs."""
    log_query = text("""
        INSERT INTO import_logs (user_id, filename, row_number, status, error_message)
        VALUES (:user_id, :filename, :row_number, :status, :error_message)
    """)
    await db.execute(
        log_query,
        {
            "user_id": user_id,
            "filename": filename,
            "row_number": row_number,
            "status": status_text,
            "error_message": error_message,
        },
    )


@router.post("/", response_model=BatchImportResponse)
async def batch_import(
    request: BatchImportRequest,
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """
    Массовая загрузка статей в базу данных с детальным логированием ошибок.

    Обрабатывает статьи по одной или батчами, логирует каждую ошибку в import_logs
    и продолжает обработку остальных статей.
    """
    # Получаем user_id
    user_id = await get_user_id(user, db)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user} not found",
        )

    total = len(request.articles)
    batch_size = request.batch_size or 100  # По умолчанию батчи по 100
    inserted_count = 0
    failed_count = 0
    errors: List[Dict[str, str]] = []

    # Обрабатываем статьи батчами
    for batch_start in range(0, total, batch_size):
        batch_end = min(batch_start + batch_size, total)
        batch_articles = request.articles[batch_start:batch_end]

        # Обрабатываем каждую статью в батче отдельно для детального логирования
        for idx, article in enumerate(batch_articles):
            row_number = batch_start + idx + 1
            title = article.title.strip()
            body = article.body.strip()

            # Валидация перед вставкой
            if len(title) < 3:
                error_msg = "Заголовок статьи слишком короткий (минимум 3 символа)"
                await log_import_error(
                    db, user_id, row_number, "validation_error", error_msg
                )
                await db.commit()
                failed_count += 1
                errors.append({"row": row_number, "error": error_msg})
                continue

            if len(body) == 0:
                error_msg = "Содержание статьи не может быть пустым"
                await log_import_error(
                    db, user_id, row_number, "validation_error", error_msg
                )
                await db.commit()
                failed_count += 1
                errors.append({"row": row_number, "error": error_msg})
                continue

            # Пытаемся вставить статью
            insert_query = text("""
                INSERT INTO articles (author_id, title, body)
                VALUES (:author_id, :title, :body)
            """)

            try:
                await db.execute(
                    insert_query,
                    {"author_id": user_id, "title": title, "body": body},
                )
                await db.commit()
                inserted_count += 1
            except IntegrityError as e:
                await db.rollback()
                error_msg = str(e.orig)

                # Определяем тип ошибки
                if "articles_title_length_check" in error_msg:
                    error_detail = (
                        "Заголовок статьи слишком короткий (минимум 3 символа)"
                    )
                elif "articles_body_not_empty_check" in error_msg:
                    error_detail = "Содержание статьи не может быть пустым"
                else:
                    error_detail = f"Нарушение целостности данных: {error_msg[:200]}"

                await log_import_error(
                    db, user_id, row_number, "integrity_error", error_detail
                )
                await db.commit()
                failed_count += 1
                errors.append({"row": row_number, "error": error_detail})
            except Exception as e:
                await db.rollback()
                error_msg = f"Внутренняя ошибка сервера: {str(e)[:200]}"
                await log_import_error(
                    db, user_id, row_number, "server_error", error_msg
                )
                await db.commit()
                failed_count += 1
                errors.append({"row": row_number, "error": error_msg})

    return BatchImportResponse(
        total=total,
        inserted=inserted_count,
        failed=failed_count,
        errors=errors[:100],  # Ограничиваем количество ошибок в ответе
    )
