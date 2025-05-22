from app.articles.models import Articles
from app.repo.base import BaseDAO


class ArticlesDAO(BaseDAO):
    model = Articles
