# app/articles/dao.py
from app.articles.models import Articles
from app.repo.base import BaseDAO


class ArticlesDAO(BaseDAO):
    model = Articles

    @classmethod
    async def find_all(cls, **filter_by):
        """Переопределяем для фильтрации удаленных статей по умолчанию"""
        # Добавляем фильтр по is_deleted, если он не указан явно
        if "is_deleted" not in filter_by:
            filter_by["is_deleted"] = False

        return await super().find_all(**filter_by)

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        """Переопределяем для фильтрации удаленных статей по умолчанию"""
        # Добавляем фильтр по is_deleted, если он не указан явно
        if "is_deleted" not in filter_by:
            filter_by["is_deleted"] = False

        return await super().find_one_or_none(**filter_by)

    @classmethod
    async def find_all_including_deleted(cls, **filter_by):
        """Специальный метод для получения всех статей, включая удаленные"""
        return await super().find_all(**filter_by)

    @classmethod
    async def find_deleted_only(cls, **filter_by):
        """Специальный метод для получения только удаленных статей"""
        filter_by["is_deleted"] = True
        return await super().find_all(**filter_by)

    @classmethod
    async def soft_delete(cls, **filter_by):
        """Мягкое удаление статьи"""
        # Убеждаемся, что обновляем только неудаленные записи
        if "is_deleted" not in filter_by:
            filter_by["is_deleted"] = False

        return await super().update(filter_by, is_deleted=True)

    @classmethod
    async def restore(cls, **filter_by):
        """Восстановление мягко удаленной статьи"""
        # При восстановлении ищем среди удаленных записей
        filter_by["is_deleted"] = True
        return await super().update(filter_by, is_deleted=False)
