# models/articles.py
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.categories import Categories
from app.models.users import Users


class Articles(Base):
    __tablename__ = "articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String, index=True)
    content: Mapped[str] = mapped_column(Text, index=True)
    image_url: Mapped[str] = mapped_column(String)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )
    is_deleted: Mapped[bool] = mapped_column(Boolean, default=False)

    # Связь с категорией
    category: Mapped["Categories"] = relationship(back_populates="articles")
    # Связь с пользователем
    user: Mapped["Users"] = relationship(back_populates="articles")


class DeletedArticles(Base):
    __tablename__ = "deleted_articles"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    original_id: Mapped[int] = mapped_column(ForeignKey("articles.id"), index=True)
    title: Mapped[str] = mapped_column(String)
    content: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(String)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime)
    updated_at: Mapped[datetime] = mapped_column(DateTime)
    deleted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
