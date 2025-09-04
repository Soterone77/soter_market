# app/articles/deleted_dao.py
from app.articles.models import DeletedArticles
from app.repo.base import BaseDAO


class DeletedArticlesDAO(BaseDAO):
    model = DeletedArticles
