# app/categories/router.py (упрощенная версия)
from fastapi import APIRouter, HTTPException, status
from typing import List

from app.categories.dao import CategoriesDAO
from app.categories.schemas import CategoryCreate, CategoryInDB

router = APIRouter(prefix="/categories", tags=["Категории"])


@router.get("/", response_model=List[CategoryInDB])
async def get_categories():
    """Получить список всех категорий"""
    return await CategoriesDAO.find_all()


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CategoryInDB)
async def create_category(category_data: CategoryCreate):
    """Создать новую категорию"""

    # Проверяем, не существует ли уже категория с таким именем
    existing_category = await CategoriesDAO.find_one_or_none(name=category_data.name)
    if existing_category:
        raise HTTPException(
            status_code=400, detail="Категория с таким названием уже существует"
        )

    # Создаем категорию
    new_category = await CategoriesDAO.add(name=category_data.name)

    if not new_category:
        raise HTTPException(status_code=500, detail="Ошибка при создании категории")

    created_category = await CategoriesDAO.find_one_or_none(id=new_category["id"])
    return created_category
