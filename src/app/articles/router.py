from fastapi import APIRouter

from app.articles.dao import ArticlesDAO
from app.articles.schemas import ArticleInDB

# from fastapi_cache.decorator import cache

router = APIRouter(prefix="/articles", tags=["Статьи"])


@router.get("/")
# @cache(expire=30)
async def get_articles() -> list[ArticleInDB]:
    return await ArticlesDAO.find_all()


@router.get("/{article_id}", include_in_schema=True)
async def get_article_by_id(
    article_id: int,
):
    return await ArticlesDAO.find_one_or_none(id=article_id)
