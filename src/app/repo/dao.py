from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.articles import Articles
from app.repo.base import BaseDAO


class ArticlesDAO(BaseDAO):
    model = Articles
