from datetime import datetime
from typing import Annotated, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_db

router = APIRouter()


class AuthorStatsResponse(BaseModel):
    author_id: str
    author_username: str
    total_articles: int
    last_article_date: Optional[datetime]
    first_article_date: Optional[datetime]


class AuthorStatsListResponse(BaseModel):
    authors: List[AuthorStatsResponse]


class CategoryStatsResponse(BaseModel):
    category_id: str
    category_name: str
    category_description: Optional[str]
    articles_count: int
    likes_count: int
    comments_count: int
    avg_weight: float
    last_article_date: Optional[datetime]
    first_article_date: Optional[datetime]


class CategoryStatsListResponse(BaseModel):
    categories: List[CategoryStatsResponse]


class ArticleReportItem(BaseModel):
    author_id: str
    author_username: str
    articles_count: int
    total_characters: int
    avg_article_length: float
    first_article_date: Optional[datetime]
    last_article_date: Optional[datetime]


class ArticleReportResponse(BaseModel):
    report: List[ArticleReportItem]


@router.get("/authors", response_model=AuthorStatsListResponse)
async def get_author_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить статистику по авторам из представления v_article_stats."""
    query = text("""
        SELECT 
            author_id,
            author_username,
            total_articles,
            last_article_date,
            first_article_date
        FROM v_article_stats
        WHERE total_articles > 0
        ORDER BY total_articles DESC
    """)

    result = await db.execute(query)
    rows = result.fetchall()

    authors = [
        AuthorStatsResponse(
            author_id=str(row.author_id),
            author_username=row.author_username,
            total_articles=row.total_articles,
            last_article_date=row.last_article_date,
            first_article_date=row.first_article_date,
        )
        for row in rows
    ]

    return AuthorStatsListResponse(authors=authors)


@router.get("/categories", response_model=CategoryStatsListResponse)
async def get_category_stats(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получить статистику по категориям из представления v_category_stats."""
    query = text("""
        SELECT 
            category_id,
            category_name,
            category_description,
            articles_count,
            likes_count,
            comments_count,
            avg_weight,
            last_article_date,
            first_article_date
        FROM v_category_stats
        ORDER BY articles_count DESC, likes_count DESC
    """)

    result = await db.execute(query)
    rows = result.fetchall()

    categories = [
        CategoryStatsResponse(
            category_id=str(row.category_id),
            category_name=row.category_name,
            category_description=row.category_description,
            articles_count=row.articles_count,
            likes_count=row.likes_count,
            comments_count=row.comments_count,
            avg_weight=float(row.avg_weight),
            last_article_date=row.last_article_date,
            first_article_date=row.first_article_date,
        )
        for row in rows
    ]

    return CategoryStatsListResponse(categories=categories)


@router.get("/report", response_model=ArticleReportResponse)
async def get_article_report(
    db: Annotated[AsyncSession, Depends(get_db)],
    start_date: Optional[datetime] = Query(None, description="Начальная дата периода"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата периода"),
):
    """Получить отчет по статьям за период с помощью функции fn_article_report."""
    query = text("""
        SELECT * FROM fn_article_report(:start_date, :end_date)
    """)

    result = await db.execute(
        query, {"start_date": start_date, "end_date": end_date}
    )
    rows = result.fetchall()

    report = [
        ArticleReportItem(
            author_id=str(row.author_id),
            author_username=row.author_username,
            articles_count=row.articles_count,
            total_characters=row.total_characters,
            avg_article_length=float(row.avg_article_length),
            first_article_date=row.first_article_date,
            last_article_date=row.last_article_date,
        )
        for row in rows
    ]

    return ArticleReportResponse(report=report)

