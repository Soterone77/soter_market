import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "article_id,status_code",
    [
        (1, 200),  # Существующая статья
        (2, 200),  # Существующая статья
        (999, 404),  # Несуществующая статья
    ],
)
async def test_get_article_by_id(
    article_id, status_code, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.get(f"/articles/{article_id}")
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "search,expected_min_count",
    [
        ("искусственный", 1),  # Должна найтись минимум 1 статья
        ("блокчейн", 1),  # Должна найтись минимум 1 статья
        ("несуществующийтекст123", 0),  # Не должно найтись
    ],
)
async def test_search_articles(
    search, expected_min_count, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.get("/articles/", params={"search": search})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= expected_min_count


@pytest.mark.parametrize(
    "category_id,expected_min_count",
    [
        (1, 2),  # Технологии - минимум 2 статьи
        (2, 1),  # Бизнес - минимум 1 статья
        (999, 0),  # Несуществующая категория
    ],
)
async def test_filter_articles_by_category(
    category_id, expected_min_count, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.get(
        "/articles/", params={"category_id": category_id}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) >= expected_min_count


@pytest.mark.parametrize(
    "page_number,page_size,expected_items",
    [
        (1, 3, 3),  # Первая страница, 3 элемента
        (2, 3, 3),  # Вторая страница, 3 элемента
        (3, 3, 0),  # Третья страница, пусто
        (1, 10, 6),  # Все статьи на одной странице
    ],
)
async def test_pagination_articles(
    page_number, page_size, expected_items, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.get(
        "/articles/", params={"page_number": page_number, "page_size": page_size}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == expected_items
    assert data["page"] == page_number
    assert data["page_size"] == page_size


async def test_create_article_unauthorized(ac: AsyncClient):
    response = await ac.post(
        "/articles/",
        data={
            "title": "Тестовая статья",
            "content": "Содержимое",
            "category_id": "1",
        },
    )
    assert response.status_code == 401


async def test_update_article_unauthorized(ac: AsyncClient):
    response = await ac.put("/articles/1", data={"title": "Новый заголовок"})
    assert response.status_code == 401


async def test_delete_article_unauthorized(ac: AsyncClient):
    response = await ac.delete("/articles/1")
    assert response.status_code == 401


@pytest.mark.parametrize(
    "article_id,status_code",
    [
        (1, 200),  # Своя статья (user_id=1 для test@test.com)
        (3, 200),  # Своя статья
        (2, 403),  # Чужая статья (user_id=2)
        (999, 404),  # Несуществующая статья
    ],
)
async def test_update_article_authorized(
    article_id, status_code, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.put(
        f"/articles/{article_id}", data={"title": "Обновленный заголовок"}
    )
    assert response.status_code == status_code


@pytest.mark.parametrize(
    "article_id,status_code",
    [
        (1, 200),  # Своя статья
        (3, 200),  # Своя статья
        (2, 403),  # Чужая статья
        (999, 404),  # Несуществующая статья
    ],
)
async def test_delete_article_authorized(
    article_id, status_code, authenticated_ac: AsyncClient
):
    response = await authenticated_ac.delete(f"/articles/{article_id}")
    assert response.status_code == status_code


async def test_get_my_articles(authenticated_ac: AsyncClient):
    response = await authenticated_ac.get("/articles/my")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    # Проверяем, что вернулись только статьи текущего пользователя
    for article in data["items"]:
        assert article["user_id"] == 1  # ID пользователя test@test.com
