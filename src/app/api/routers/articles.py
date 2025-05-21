from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Query
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.articles import Articles
from app.repo.dao import ArticlesDAO

# from fastapi_cache.decorator import cache

router = APIRouter(prefix="/articles", tags=["Статьи"])


@router.get("/")
# @cache(expire=30)
async def get_articles():
    return await ArticlesDAO.find_all()


@router.get("/{article_id}", include_in_schema=True)
async def get_article_by_id(
    article_id: int,
):
    pass
