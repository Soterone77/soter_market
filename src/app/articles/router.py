# app/articles/router.py
from fastapi import APIRouter, Depends, HTTPException, Query, status
from typing import Annotated, Optional
from datetime import datetime
import math

from app.articles.dao import ArticlesDAO
from app.articles.deleted_dao import DeletedArticlesDAO
from app.articles.schemas import (
    ArticleInDB,
    ArticleCreate,
    ArticleUpdate,
    DeletedArticleInDB,
    ArticleListResponse,  # Импортируем новую схему
)
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/articles", tags=["Статьи"])

# Максимальное количество элементов на странице
MAX_PAGE_SIZE = 100


@router.get("/", response_model=ArticleListResponse)  # Изменяем response_model
async def get_articles(
    search: Annotated[
        Optional[str], Query(description="Поиск по заголовку и содержимому")
    ] = None,
    category_id: Annotated[
        Optional[int], Query(description="Фильтр по категории")
    ] = None,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=MAX_PAGE_SIZE, description="Размер страницы")
    ] = 10,
) -> ArticleListResponse:
    """Получить все статьи с пагинацией и поиском"""

    # Получаем статьи с пагинацией
    articles, total = await ArticlesDAO.find_with_pagination(
        page=page_number, page_size=page_size, search=search, category_id=category_id
    )

    # Вычисляем метаданные пагинации
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    has_next = page_number < total_pages
    has_prev = page_number > 1

    return ArticleListResponse(
        items=articles,
        total=total,
        page=page_number,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )


@router.get("/my", response_model=ArticleListResponse)  # Изменяем response_model
async def get_my_articles(
    user: Users = Depends(get_current_user),
    search: Annotated[
        Optional[str], Query(description="Поиск по заголовку и содержимому")
    ] = None,
    category_id: Annotated[
        Optional[int], Query(description="Фильтр по категории")
    ] = None,
    page_number: Annotated[int, Query(ge=1, description="Номер страницы")] = 1,
    page_size: Annotated[
        int, Query(ge=1, le=MAX_PAGE_SIZE, description="Размер страницы")
    ] = 10,
) -> ArticleListResponse:
    """Получить мои статьи с пагинацией и поиском"""

    # Получаем статьи пользователя с пагинацией
    articles, total = await ArticlesDAO.find_with_pagination(
        page=page_number,
        page_size=page_size,
        search=search,
        category_id=category_id,
        user_id=user.id,
    )

    # Вычисляем метаданные пагинации
    total_pages = math.ceil(total / page_size) if total > 0 else 1
    has_next = page_number < total_pages
    has_prev = page_number > 1

    return ArticleListResponse(
        items=articles,
        total=total,
        page=page_number,
        page_size=page_size,
        total_pages=total_pages,
        has_next=has_next,
        has_prev=has_prev,
    )


# Остальные методы остаются без изменений
@router.get("/{article_id}")
async def get_article_by_id(article_id: int):
    """Получить статью по ID"""
    article = await ArticlesDAO.find_one_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_article(
    article_data: ArticleCreate, user: Users = Depends(get_current_user)
) -> ArticleInDB:
    """Создать новую статью"""

    # Создаем статью с автоматическим добавлением user_id
    new_article = await ArticlesDAO.add(
        title=article_data.title,
        content=article_data.content,
        image_url=article_data.image_url,
        category_id=article_data.category_id,
        user_id=user.id,
    )

    if not new_article:
        raise HTTPException(status_code=500, detail="Ошибка при создании статьи")

    # Получаем полную информацию о созданной статье
    created_article = await ArticlesDAO.find_one_or_none(id=new_article["id"])
    return created_article


@router.put("/{article_id}")
async def update_article(
    article_id: int,
    article_data: ArticleUpdate,
    user: Users = Depends(get_current_user),
) -> ArticleInDB:
    """Обновить статью (только свою)"""

    # Проверяем, существует ли статья
    existing_article = await ArticlesDAO.find_one_or_none(id=article_id)
    if not existing_article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    # Проверяем, что статья принадлежит текущему пользователю
    if existing_article["user_id"] != user.id:
        raise HTTPException(
            status_code=403, detail="Нет прав для редактирования этой статьи"
        )

    # Подготавливаем данные для обновления (только переданные поля)
    update_data = article_data.model_dump(exclude_unset=True)
    if update_data:  # Если есть что обновлять
        update_data["updated_at"] = datetime.utcnow()

        # Обновляем статью
        updated_article = await ArticlesDAO.update(
            filter_by={"id": article_id}, **update_data
        )

        if not updated_article:
            raise HTTPException(status_code=500, detail="Ошибка при обновлении статьи")

        return updated_article

    # Если нечего обновлять, возвращаем текущую статью
    return existing_article


@router.delete("/{article_id}")
async def delete_article(article_id: int, user: Users = Depends(get_current_user)):
    """Удалить статью (только свою) - настоящее фейковое удаление"""

    # Проверяем, существует ли статья
    existing_article = await ArticlesDAO.find_one_or_none(id=article_id)
    if not existing_article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    # Проверяем, что статья принадлежит текущему пользователю
    if existing_article["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Нет прав для удаления этой статьи")

    # Выполняем настоящее фейковое удаление (перемещение в deleted_articles)
    deleted_article = await ArticlesDAO.hard_fake_delete(article_id)

    if not deleted_article:
        raise HTTPException(status_code=500, detail="Ошибка при удалении статьи")

    return {"message": "Статья успешно удалена"}
