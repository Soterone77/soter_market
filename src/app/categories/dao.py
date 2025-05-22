from app.categories.models import Categories
from app.repo.base import BaseDAO


class CategoriesDAO(BaseDAO):
    model = Categories
