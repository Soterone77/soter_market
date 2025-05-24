from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import func, or_, select

from app.articles.deleted_dao import DeletedArticlesDAO
from app.articles.models import Articles
from app.core.database import async_session_maker
from app.repo.base import BaseDAO


class ArticlesDAO(BaseDAO):
    model = Articles

    @classmethod
    async def find_with_pagination(
        cls,
        page: int = 1,
        page_size: int = 10,
        search: Optional[str] = None,
        category_id: Optional[int] = None,
        user_id: Optional[int] = None,
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Найти статьи с пагинацией, поиском и фильтрацией
        Возвращает кортеж (список_статей, общее_количество)
        """
        async with async_session_maker() as session:
            # Базовый запрос
            query = select(cls.model.__table__.columns)
            count_query = select(func.count(cls.model.id))

            # Фильтр по категории
            if category_id:
                query = query.where(cls.model.category_id == category_id)
                count_query = count_query.where(cls.model.category_id == category_id)

            # Фильтр по пользователю
            if user_id:
                query = query.where(cls.model.user_id == user_id)
                count_query = count_query.where(cls.model.user_id == user_id)

            # Полнотекстовый поиск PostgreSQL
            if search:
                search_condition = or_(
                    func.to_tsvector("russian", cls.model.title).op("@@")(
                        func.plainto_tsquery("russian", search)
                    ),
                    func.to_tsvector("russian", cls.model.content).op("@@")(
                        func.plainto_tsquery("russian", search)
                    ),
                )
                query = query.where(search_condition)
                count_query = count_query.where(search_condition)

            # Получаем общее количество записей
            total_result = await session.execute(count_query)
            total = total_result.scalar()

            # Добавляем пагинацию и сортировку
            offset = (page - 1) * page_size
            # сортируем по ID в возрастающем порядке (или по created_at.asc())
            query = query.order_by(cls.model.id.asc()).offset(offset).limit(page_size)

            # Выполняем запрос
            result = await session.execute(query)
            articles = result.mappings().all()

            return articles, total

    @classmethod
    async def hard_fake_delete(cls, article_id: int):
        """Настоящее фейковое удаление"""
        async with async_session_maker() as session:
            try:
                # 1. Получаем статью для удаления
                article = await cls.find_one_or_none(id=article_id)
                if not article:
                    return None

                # 2. Создаем запись в deleted_articles
                deleted_article_data = {
                    "title": article["title"],
                    "content": article["content"],
                    "image_url": article["image_url"],
                    "category_id": article["category_id"],
                    "user_id": article["user_id"],
                    "created_at": article["created_at"],
                    "updated_at": article["updated_at"],
                    "deleted_at": datetime.utcnow(),
                }

                deleted_article = await DeletedArticlesDAO.add(**deleted_article_data)
                if not deleted_article:
                    return None

                # 3. Удаляем статью из основной таблицы
                await cls.delete(id=article_id)

                return deleted_article

            except Exception as e:
                await session.rollback()
                raise e
