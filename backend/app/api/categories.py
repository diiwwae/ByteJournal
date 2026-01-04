from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.utils import get_current_user
from app.db import get_db

router = APIRouter()


class CategoryCreate(BaseModel):
    name: str = Field(..., min_length=2, description="Название категории")
    description: Optional[str] = Field(None, description="Описание категории")
    color: Optional[str] = Field(
        None, pattern="^#[0-9A-Fa-f]{6}$", description="Цвет в формате HEX (#RRGGBB)"
    )


class CategoryResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    color: Optional[str]
    created_at: datetime
    updated_at: datetime


class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]


async def get_user_role(username: str, db: AsyncSession) -> Optional[str]:
    """Получить роль пользователя по username."""
    query = text("""
        SELECT r.name 
        FROM users u
        JOIN roles r ON u.role_id = r.id
        WHERE u.username = :u
    """)
    result = await db.execute(query, {"u": username})
    row = result.fetchone()
    return row[0] if row else None


async def require_role(
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
    allowed_roles: List[str],
) -> str:
    """Проверяет, что пользователь имеет одну из разрешенных ролей."""
    role = await get_user_role(user, db)
    if role not in allowed_roles:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Требуется одна из ролей: {', '.join(allowed_roles)}",
        )
    return user


@router.get("/", response_model=CategoryListResponse)
async def list_categories(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить список всех категорий."""
    query = text("""
        SELECT id, name, description, color, created_at, updated_at
        FROM categories
        ORDER BY name
    """)
    result = await db.execute(query)
    rows = result.fetchall()

    categories = [
        CategoryResponse(
            id=str(row.id),
            name=row.name,
            description=row.description,
            color=row.color,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
        for row in rows
    ]

    return CategoryListResponse(categories=categories)


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить информацию о категории по ID."""
    query = text("""
        SELECT id, name, description, color, created_at, updated_at
        FROM categories
        WHERE id = :id
    """)
    result = await db.execute(query, {"id": category_id})
    row = result.fetchone()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )

    return CategoryResponse(
        id=str(row.id),
        name=row.name,
        description=row.description,
        color=row.color,
        created_at=row.created_at,
        updated_at=row.updated_at,
    )


@router.post("/", response_model=CategoryResponse)
async def create_category(
    category_in: CategoryCreate,
    user: Annotated[str, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Создать новую категорию (только для авторов и администраторов)."""
    # Проверяем роль
    await require_role(user, db, ["author", "admin"])

    query = text("""
        INSERT INTO categories (name, description, color)
        VALUES (:name, :description, :color)
        RETURNING id, name, description, color, created_at, updated_at
    """)

    try:
        result = await db.execute(
            query,
            {
                "name": category_in.name.strip(),
                "description": category_in.description.strip()
                if category_in.description
                else None,
                "color": category_in.color,
            },
        )
        await db.commit()
        row = result.fetchone()

        if not row:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при создании категории",
            )

        return CategoryResponse(
            id=str(row.id),
            name=row.name,
            description=row.description,
            color=row.color,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )
    except IntegrityError as e:
        await db.rollback()
        error_msg = str(e.orig)

        if "categories_name_key" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Категория с таким названием уже существует",
            )
        elif "categories_name_length_check" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Название категории слишком короткое (минимум 2 символа)",
            )
        elif "categories_color_format_check" in error_msg:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Неверный формат цвета (должен быть #RRGGBB)",
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ошибка при создании категории",
        )
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Внутренняя ошибка сервера: {str(e)}",
        )
