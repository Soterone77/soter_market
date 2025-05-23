# app/articles/router.py
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
    status,
    UploadFile,
    File,
    Form,
)
from typing import Annotated, Optional
from datetime import datetime
import math
import uuid
import os

from app.articles.dao import ArticlesDAO
from app.articles.deleted_dao import DeletedArticlesDAO
from app.articles.schemas import (
    ArticleInDB,
    ArticleCreate,
    ArticleUpdate,
    DeletedArticleInDB,
    ArticleListResponse,
)
from app.users.dependencies import get_current_user
from app.users.models import Users
from app.services.s3_client import S3Client
from app.core.config import settings

router = APIRouter(prefix="/articles", tags=["Статьи"])

# Максимальное количество элементов на странице
MAX_PAGE_SIZE = 100

# Разрешенные типы изображений
ALLOWED_IMAGE_TYPES = ["image/jpeg", "image/png", "image/gif", "image/webp"]
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB


# Инициализация S3 клиента
s3_client = S3Client(
    access_key=settings.S3_ACCESS_KEY,
    secret_key=settings.S3_SECRET_KEY,
    endpoint_url=settings.S3_ENDPOINT_URL,
    bucket_name=settings.S3_BUCKET_NAME,
)


@router.get("/", response_model=ArticleListResponse)
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


@router.get("/my", response_model=ArticleListResponse)
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


@router.get("/{article_id}")
async def get_article_by_id(article_id: int):
    """Получить статью по ID"""
    article = await ArticlesDAO.find_one_or_none(id=article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Статья не найдена")
    return article


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_article(
    title: Annotated[str, Form(description="Название статьи")],
    content: Annotated[str, Form(description="Содержимое статьи")],
    category_id: Annotated[int, Form(description="ID категории")],
    image: Annotated[
        Optional[UploadFile], File(description="Изображение статьи")
    ] = None,
    user: Users = Depends(get_current_user),
) -> ArticleInDB:
    """Создать новую статью с возможностью загрузки изображения"""

    image_url = None

    # Обработка изображения, если оно загружено
    if image:
        # Проверка типа файла
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        # Проверка размера файла
        contents = await image.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Файл слишком большой. Максимальный размер: {MAX_IMAGE_SIZE // 1024 // 1024} MB",
            )

        # Генерация уникального имени файла
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"articles/{user.id}/{uuid.uuid4()}{file_extension}"

        try:
            # Загрузка в S3
            await s3_client.upload_file_from_memory(contents, unique_filename)
            image_url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{unique_filename}"
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Ошибка при загрузке изображения: {str(e)}"
            )

    new_article = await ArticlesDAO.add(
        title=title,
        content=content,
        image_url=image_url,
        category_id=category_id,
        user_id=user.id,
    )

    if not new_article:
        # Если создание статьи не удалось, удаляем загруженное изображение
        if image_url:
            try:
                await s3_client.delete_file(unique_filename)
            except:
                pass  # Игнорируем ошибки удаления
        raise HTTPException(status_code=500, detail="Ошибка при создании статьи")

    # Получаем полную информацию о созданной статье
    created_article = await ArticlesDAO.find_one_or_none(id=new_article["id"])
    return created_article


@router.put("/{article_id}")
async def update_article(
    article_id: int,
    title: Annotated[Optional[str], Form()] = None,
    content: Annotated[Optional[str], Form()] = None,
    category_id: Annotated[Optional[int], Form()] = None,
    image: Annotated[Optional[UploadFile], File()] = None,
    user: Users = Depends(get_current_user),
) -> ArticleInDB:
    """Обновить статью (только свою) с возможностью изменения изображения"""

    # Проверяем, существует ли статья
    existing_article = await ArticlesDAO.find_one_or_none(id=article_id)
    if not existing_article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    # Проверяем, что статья принадлежит текущему пользователю
    if existing_article["user_id"] != user.id:
        raise HTTPException(
            status_code=403, detail="Нет прав для редактирования этой статьи"
        )

    # Подготавливаем данные для обновления
    update_data = {}
    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["content"] = content
    if category_id is not None:
        update_data["category_id"] = category_id

    # Обработка нового изображения
    if image:
        # Проверки как в create_article
        if image.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(
                status_code=400,
                detail=f"Недопустимый тип файла. Разрешены: {', '.join(ALLOWED_IMAGE_TYPES)}",
            )

        contents = await image.read()
        if len(contents) > MAX_IMAGE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"Файл слишком большой. Максимальный размер: {MAX_IMAGE_SIZE // 1024 // 1024} MB",
            )

        # Генерация уникального имени файла
        file_extension = os.path.splitext(image.filename)[1]
        unique_filename = f"articles/{user.id}/{uuid.uuid4()}{file_extension}"

        try:
            # Загрузка нового изображения
            await s3_client.upload_file_from_memory(contents, unique_filename)
            new_image_url = f"{settings.S3_ENDPOINT_URL}/{settings.S3_BUCKET_NAME}/{unique_filename}"

            # Удаление старого изображения, если оно есть
            if existing_article.get("image_url"):
                old_filename = existing_article["image_url"].split("/")[-1]
                try:
                    await s3_client.delete_file(f"articles/{user.id}/{old_filename}")
                except:
                    pass  # Игнорируем ошибки удаления старого файла

            update_data["image_url"] = new_image_url
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Ошибка при загрузке изображения: {str(e)}"
            )

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
