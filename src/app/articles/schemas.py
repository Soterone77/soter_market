# app/schemas/articles.py
from datetime import datetime

from pydantic import BaseModel

from app.categories.schemas import Category
from app.users.schemas import User


class ArticleBase(BaseModel):
    """Базовая схема статьи."""

    title: str
    content: str
    image_url: str
    category_id: int


class ArticleCreate(ArticleBase):
    """Схема для создания статьи."""


class ArticleUpdate(BaseModel):
    """Схема для обновления статьи."""

    title: str | None = None
    content: str | None = None
    image_url: str | None = None
    category_id: int | None = None


class ArticleInDB(ArticleBase):
    """Схема статьи в БД."""

    id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Article(ArticleInDB):
    """Полная схема статьи для ответов API."""

    category: Category
    user: User


class ArticleListResponse(BaseModel):
    """Схема для списка статей с пагинацией."""

    items: list[ArticleInDB]
    total: int
    page: int
    page_size: int
    total_pages: int
    has_next: bool
    has_prev: bool


class DeletedArticleBase(BaseModel):
    """Базовая схема удаленной статьи."""

    title: str
    content: str
    image_url: str
    category_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime


class DeletedArticleInDB(DeletedArticleBase):
    """Схема удаленной статьи в БД."""

    id: int
    deleted_at: datetime

    class Config:
        from_attributes = True


class DeletedArticle(DeletedArticleInDB):
    """Полная схема удаленной статьи для ответов API."""
