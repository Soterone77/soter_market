# System Design: soter_market

## Оглавление
1. [Структура и архитектура](#структура-и-архитектура)
2. [Технический стек](#технический-стек)
3. [Бизнес-логика и контракты](#бизнес-логика-и-контракты)
4. [Качество кода и процессы](#качество-кода-и-процессы)
5. [Безопасность и производительность](#безопасность-и-производительность)
6. [Deployment и инфраструктура](#deployment-и-инфраструктура)
7. [Проблемные зоны и рекомендации](#проблемные-зоны-и-рекомендации)

---

## 1. Структура и архитектура

### Дерево проекта с пояснениями

```
soter_market/
│
├── docker-compose.yml         # Описание инфраструктуры (БД, Redis, etc.)
├── Dockerfile                 # Сборка образа приложения
├── pyproject.toml             # Основные зависимости и настройки Poetry
├── README.md                  # Документация по проекту
├── src/
│   ├── alembic.ini            # Конфиг миграций Alembic
│   ├── app/
│   │   ├── __init__.py
│   │   ├── articles/          # Модуль бизнес-логики "Статьи"
│   │   │   ├── dao.py         # DAO-слой для работы с БД
│   │   │   ├── deleted_dao.py # DAO для удалённых статей
│   │   │   ├── models.py      # SQLAlchemy-модели статей
│   │   │   ├── router.py      # FastAPI-роуты для статей
│   │   │   └── schemas.py     # Pydantic-схемы для валидации
│   │   ├── categories/        # Модуль бизнес-логики "Категории"
│   │   │   ├── dao.py
│   │   │   ├── models.py
│   │   │   ├── router.py
│   │   │   └── schemas.py
│   │   ├── core/              # Ядро приложения: настройки, БД
│   │   │   ├── config.py      # Конфиг через Pydantic BaseSettings
│   │   │   └── database.py    # Инициализация SQLAlchemy
│   │   ├── exceptions.py      # Кастомные исключения
│   │   ├── logger.py          # Логирование (json-формат)
│   │   ├── main.py            # Главная точка входа FastAPI
│   │   ├── migrations/        # Миграции Alembic
│   │   ├── repo/              # Базовые DAO-абстракции
│   │   ├── services/          # Внешние сервисы (например, S3)
│   │   ├── tasks/             # Celery-задачи и email-шаблоны
│   │   └── users/             # Модуль "Пользователи" (auth, модели, роуты)
│   ├── conftest.py            # Общие фикстуры для тестов
│   ├── pytest.ini             # Настройки pytest
│   └── tests/                 # Тесты (unit/integration)
│       ├── integration_tests/
│       └── unit_tests/
└── test_main.http             # Примеры HTTP-запросов для тестирования API
```

### Архитектурный паттерн

- Преобладает паттерн "Layered Architecture" (многослойная архитектура) с элементами DDD:
  - Внешний слой: FastAPI-роутеры (REST API)
  - Сервисный слой: бизнес-логика, интеграции (services, tasks)
  - DAO/репозиторий: доступ к данным через DAO-абстракции
  - Модели: SQLAlchemy ORM
  - Схемы: Pydantic для валидации и сериализации

- **Точки входа**:
  - `src/app/main.py` — основной entrypoint FastAPI-приложения
  - `src/app/tasks/celery_app.py` — точка входа для Celery worker
  - `docker-compose.yml` и `Dockerfile` — для деплоя и запуска инфраструктуры

### Слои приложения и их взаимодействие

- **API-слой** (`router.py`): принимает HTTP-запросы, валидирует входные данные через Pydantic-схемы, вызывает бизнес-логику.
- **Бизнес-логика/сервисы** (`services/`, `tasks/`): реализует интеграции (например, S3, email), асинхронные задачи (Celery).
- **DAO/репозитории** (`dao.py`, `repo/base.py`): инкапсулируют работу с БД через SQLAlchemy.
- **Модели** (`models.py`): описывают структуру таблиц и связи.
- **Конфигурация и инфраструктура** (`core/`, `migrations/`, `logger.py`): настройки, подключение к БД, миграции, логирование.

---

## 2. Технический стек

### Основные зависимости (pyproject.toml)
- FastAPI — основной web-фреймворк для построения REST API
- SQLAlchemy — ORM для работы с реляционной БД
- asyncpg — асинхронный драйвер PostgreSQL
- alembic — миграции БД
- Pydantic (через pydantic-settings) — валидация и управление конфигами
- Celery — асинхронные задачи (фоновые процессы)
- Redis — брокер и backend для Celery, кэширование
- aiobotocore — асинхронная работа с S3-совместимыми хранилищами
- python-jose — работа с JWT (аутентификация)
- bcrypt — хеширование паролей
- gunicorn + uvicorn — продакшн-сервер для запуска FastAPI
- pytest, pytest-asyncio — тестирование
- fastapi-cache2 — кэширование на уровне API
- flower — мониторинг задач Celery
- pillow — работа с изображениями

### Версия Python
- Python >= 3.13 (указано в pyproject.toml и Dockerfile)

### Используемые фреймворки и библиотеки
- FastAPI, SQLAlchemy 2.x, Pydantic, Celery, aiobotocore, pytest

### ORM и базы данных
- PostgreSQL (через asyncpg и SQLAlchemy)
- Alembic — миграции

### Инфраструктурные компоненты (docker-compose.yml)
- PostgreSQL 15 — основная БД
- Redis 7 — брокер и backend для Celery, кэш
- market_app — приложение FastAPI
- Celery worker и Celery beat — обработка фоновых и периодических задач
- S3-совместимое хранилище — интеграция через переменные окружения

### Сборка и запуск (Dockerfile)
- Официальный образ python:3.13-slim
- Установка зависимостей через uv
- Копирование исходного кода
- Запуск через uvicorn (или gunicorn+uvicorn worker)
- Переменные окружения: PYTHONPATH, PATH

---

## 3. Бизнес-логика и контракты

### Основные бизнес-сущности и их модели

- **User (Пользователь)**: id, email, hashed_password, is_active, created_at, updated_at, articles
- **Article (Статья)**: id, title, content, image_url, category_id, user_id, created_at, updated_at, category, user
- **Category (Категория)**: id, name, created_at, updated_at, articles
- **DeletedArticle (Удалённая статья)**: аналогична Article, но с полем deleted_at

### API-контракты (эндпоинты и их назначение)

#### /auth (Аутентификация)
- POST /auth/register — регистрация пользователя, отправка email через Celery
- POST /auth/login — вход, выдача JWT-токена (cookie)
- POST /auth/logout — выход (удаление cookie)

#### /users (Пользователи)
- GET /users/me — получить текущего пользователя (по токену)

#### /articles (Статьи)
- GET /articles/ — список статей с пагинацией, поиском, фильтрацией по категории
- GET /articles/my — список статей текущего пользователя
- GET /articles/{article_id} — получить статью по ID
- POST /articles/ — создать статью (title, content, category_id, image), загрузка изображения в S3
- PUT /articles/{article_id} — обновить статью (только свою), поддержка смены изображения
- DELETE /articles/{article_id} — "мягкое" удаление статьи (перемещение в deleted_articles)

#### /categories (Категории)
- GET /categories/ — список всех категорий
- POST /categories/ — создать новую категорию

### Примеры запросов/ответов

- POST /auth/register: `{ "email": "user@example.com", "password": "123456" }` → `{ "message": "Пользователь успешно зарегистрирован" }`
- POST /auth/login: `{ "email": "user@example.com", "password": "123456" }` → `{ "access_token": "<jwt>" }`
- POST /articles/: multipart form (title, content, category_id, image) → JSON с полной информацией о статье

### Внешние интеграции и их контракты

- **S3 (aiobotocore)**: загрузка/удаление файлов, переменные окружения для доступа
- **Email (Celery + SMTP)**: асинхронная отправка писем при регистрации, SMTP-конфиг

---

## 4. Качество кода и процессы

### Покрытие тестами и структура тестов
- Тесты разделены на unit и integration
- Асинхронные фикстуры для подготовки БД, клиента, аутентификации
- Покрытие: CRUD, авторизация, пагинация, фильтрация, права доступа
- Используется pytest и pytest-asyncio

### Конфигурационные файлы
- .env-non-dev — переменные окружения
- src/app/core/config.py — централизованная конфигурация через Pydantic BaseSettings
- alembic.ini — настройки миграций
- pyproject.toml — зависимости, настройки инструментов разработки
- docker-compose.yml, Dockerfile — инфраструктура и сборка

### CI/CD и процессы разработки
- pre-commit — автоматический запуск линтеров, форматтеров, проверок стиля
- ruff — основной инструмент для lint/format
- pytest — тестирование
- poetry/uv — управление зависимостями
- Документация: README.md, OpenAPI (Swagger, ReDoc)

### Документация и docstrings
- README.md — подробный, структурированный, с примерами команд, переменных, ссылками на API-доки
- Docstrings — присутствуют в ключевых функциях и роутерах
- OpenAPI — генерируется автоматически FastAPI

---

## 5. Безопасность и производительность

### Аутентификация и авторизация
- JWT-аутентификация (python-jose), токен в HTTP-only cookie, срок жизни 30 мин
- Хеширование паролей через bcrypt
- Middleware для проверки токена, Depends(get_current_user) для защищённых эндпоинтов
- Проверка прав на изменение/удаление сущностей на уровне бизнес-логики

### Логирование и мониторинг
- Логирование: logging + python-json-logger, формат JSON, уровень через LOG_LEVEL
- Мониторинг Celery: Flower
- Sentry: переменная SENTRY_DSN (интеграция возможна)

### Кэширование
- Redis: брокер и backend для Celery, fastapi-cache2 для кэширования API
- Потенциал для расширения кэширования (например, списки статей)

### Потенциальные узкие места производительности
- Асинхронность всего стека (FastAPI, SQLAlchemy, asyncpg, aiobotocore)
- Работа с файлами (S3): возможны задержки при большом количестве операций
- База данных: индексация, сложные JOIN, лимиты пагинации
- Фоновые задачи: мониторинг очередей и ресурсов Redis

---

## 6. Deployment и инфраструктура

### Dockerfile и docker-compose
- Dockerfile: python:3.13-slim, uv, копирование кода, запуск через uvicorn/gunicorn
- docker-compose.yml: сервисы db (PostgreSQL), redis, market (FastAPI), celery, celery_beat
- Volume для данных PostgreSQL

### Миграции и деплой
- Alembic: миграции в src/app/migrations, alembic upgrade head при старте контейнера
- Запуск: docker-compose up --build (production/dev), poetry/uv + alembic + fastapi dev (локально)

### Переменные окружения
- MODE, LOG_LEVEL, DB_*, SMTP_*, REDIS_*, SENTRY_DSN, SECRET_KEY, ALGORITHM, S3_*, CELERY_*

### Масштабирование
- Горизонтальное масштабирование: несколько экземпляров market/celery
- Redis и PostgreSQL могут быть вынесены на managed-сервисы
- Балансировка нагрузки: внешний балансировщик (nginx, cloud LB)
- Мониторинг: Flower, Sentry, логи в формате JSON

---

## 7. Проблемные зоны и рекомендации

### Технический долг и устаревший код
- Регулярно обновлять зависимости (FastAPI, SQLAlchemy, Celery)
- Ревизовать неиспользуемые DAO/сервисы (например, deleted_dao.py)
- Логировать все ошибки, не использовать pass
- Нет системы ролей/прав доступа (RBAC), только проверка "владелец/не владелец"

### Сложные участки без документации
- Внешние интеграции (S3, Celery, email) требуют внимательного изучения
- Миграции Alembic и структура моделей требуют понимания SQLAlchemy 2.x
- Нет отдельной папки docs/

### Архитектурные рекомендации
- Документировать архитектурные решения (ADR или в README)
- Вынести интеграции (S3, email) в отдельные сервисные слои с интерфейсами
- Добавить роли и права (RBAC)
- Реализовать централизованный мониторинг (Sentry, Prometheus, Grafana)
- Покрыть тестами все критичные бизнес-сценарии
- Добавить healthchecks для всех сервисов и endpoint /health

### План изучения проекта для нового разработчика
1. Изучить README.md
2. Посмотреть main.py и роутеры
3. Изучить модели и DAO
4. Понять работу с конфигами
5. Изучить тесты
6. Изучить инфраструктуру
7. Понять интеграции
8. Ознакомиться с документацией API

### Ключевые файлы для понимания архитектуры
- src/app/main.py
- src/app/core/config.py
- src/app/articles/models.py, src/app/users/models.py, src/app/categories/models.py
- src/app/articles/router.py, src/app/users/router.py, src/app/categories/router.py
- src/app/repo/base.py
- src/app/services/s3_client.py, src/app/tasks/tasks.py
- src/tests/
- docker-compose.yml, Dockerfile
