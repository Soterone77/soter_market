# app/articles/dao.py
from datetime import datetime
from app.articles.models import Articles, DeletedArticles
from app.articles.deleted_dao import DeletedArticlesDAO
from app.repo.base import BaseDAO
from app.core.database import async_session_maker


class ArticlesDAO(BaseDAO):
    model = Articles

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
