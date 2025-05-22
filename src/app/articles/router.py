from fastapi import APIRouter, Depends, HTTPException, Request, status
from datetime import datetime

from app.articles.dao import ArticlesDAO
from app.articles.schemas import ArticleInDB, ArticleCreate, ArticleUpdate
from app.users.dependencies import get_current_user
from app.users.models import Users

router = APIRouter(prefix="/articles", tags=["Статьи"])


@router.get("/")
async def get_articles() -> list[ArticleInDB]:
    """Получить все статьи"""
    return await ArticlesDAO.find_all()


@router.get("/my")
async def get_my_articles(
    user: Users = Depends(get_current_user),
) -> list[ArticleInDB]:
    """Получить мои статьи"""
    return await ArticlesDAO.find_all(user_id=user.id)


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
    """Удалить статью (только свою) - мягкое удаление"""

    # Проверяем, существует ли статья
    existing_article = await ArticlesDAO.find_one_or_none(id=article_id)
    if not existing_article:
        raise HTTPException(status_code=404, detail="Статья не найдена")

    # Проверяем, что статья принадлежит текущему пользователю
    if existing_article["user_id"] != user.id:
        raise HTTPException(status_code=403, detail="Нет прав для удаления этой статьи")

    # Проверяем, не удалена ли уже статья
    if existing_article["is_deleted"]:
        raise HTTPException(status_code=410, detail="Статья уже удалена")

    # Помечаем статью как удаленную
    deleted_article = await ArticlesDAO.update(
        filter_by={"id": article_id}, is_deleted=True, updated_at=datetime.utcnow()
    )

    if not deleted_article:
        raise HTTPException(status_code=500, detail="Ошибка при удалении статьи")

    return {"message": "Статья успешно удалена"}
