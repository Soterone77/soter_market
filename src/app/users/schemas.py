# schemas/models.py
from datetime import datetime

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    """Базовая схема пользователя."""

    email: EmailStr


class UserCreate(UserBase):
    """Схема для создания пользователя."""

    password: str


class UserAuth(UserBase):
    """Схема для создания пользователя."""

    password: str


class UserUpdate(BaseModel):
    """Схема для обновления пользователя."""

    email: EmailStr | None = None
    password: str | None = None
    is_active: bool | None = None


class UserInDB(UserBase):
    """Схема пользователя в БД."""

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class User(UserInDB):
    """Полная схема пользователя для ответов API."""
