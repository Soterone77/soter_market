# schemas/models.py
from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CategoryBase(BaseModel):
    """Базовая схема категории."""

    name: str


class CategoryCreate(CategoryBase):
    """Схема для создания категории."""

    pass


class CategoryUpdate(CategoryBase):
    """Схема для обновления категории."""

    name: Optional[str] = None


class CategoryInDB(CategoryBase):
    """Схема категории в БД."""

    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Category(CategoryInDB):
    """Полная схема категории для ответов API."""

    pass
