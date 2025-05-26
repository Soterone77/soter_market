import asyncio
import json
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.articles.models import Articles, DeletedArticles
from app.categories.models import Categories
from app.core.config import settings
from app.core.database import Base, async_session_maker, engine
from app.main import app as fastapi_app
from app.users.models import Users


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    # Обязательно убеждаемся, что работаем с тестовой БД
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        # Удаление всех заданных нами таблиц из БД
        await conn.run_sync(Base.metadata.drop_all)
        # Добавление всех заданных нами таблиц из БД
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f"tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    users = open_mock_json("users")
    categories = open_mock_json("categories")
    articles = open_mock_json("articles")
    deleted_articles = open_mock_json("deleted_articles")

    # Форматирование дат для categories
    for category in categories:
        category["created_at"] = datetime.strptime(
            category["created_at"], "%Y-%m-%dT%H:%M:%S"
        )
        category["updated_at"] = datetime.strptime(
            category["updated_at"], "%Y-%m-%dT%H:%M:%S"
        )

    # Форматирование дат для articles
    for article in articles:
        article["created_at"] = datetime.strptime(
            article["created_at"], "%Y-%m-%dT%H:%M:%S"
        )
        article["updated_at"] = datetime.strptime(
            article["updated_at"], "%Y-%m-%dT%H:%M:%S"
        )

    # Форматирование дат для deleted_articles
    for deleted_article in deleted_articles:
        deleted_article["created_at"] = datetime.strptime(
            deleted_article["created_at"], "%Y-%m-%dT%H:%M:%S"
        )
        deleted_article["updated_at"] = datetime.strptime(
            deleted_article["updated_at"], "%Y-%m-%dT%H:%M:%S"
        )
        deleted_article["deleted_at"] = datetime.strptime(
            deleted_article["deleted_at"], "%Y-%m-%dT%H:%M:%S"
        )

    async with async_session_maker() as session:
        # ВАЖНО: соблюдаем порядок вставки из-за foreign keys
        # 1. Сначала Users (независимая таблица)
        await session.execute(insert(Users).values(users))

        # 2. Затем Categories (независимая таблица)
        await session.execute(insert(Categories).values(categories))

        # 3. Articles (зависит от Users и Categories)
        await session.execute(insert(Articles).values(articles))

        # 4. DeletedArticles (зависит от Users и Categories)
        await session.execute(insert(DeletedArticles).values(deleted_articles))

        await session.commit()


# Создаем новый event loop для прогона тестов
@pytest.fixture(scope="session")
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def ac():
    "Асинхронный клиент для тестирования эндпоинтов"
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture(scope="session")
async def authenticated_ac():
    "Асинхронный аутентифицированный клиент для тестирования эндпоинтов"
    transport = ASGITransport(app=fastapi_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        await client.post(
            "/auth/login",
            json={
                "email": "test@test.com",
                "password": "test",
            },
        )
        assert client.cookies["market_access_token"]
        yield client
