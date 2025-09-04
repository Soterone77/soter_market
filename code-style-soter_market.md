# Code Style и паттерны проекта soter_market

## Оглавление
1. [Анализ стиля кодирования](#анализ-стиля-кодирования)
2. [Архитектурные паттерны](#архитектурные-паттерны)
3. [Структура и организация кода](#структура-и-организация-кода)
4. [Типизация и современные практики](#типизация-и-современные-практики)
5. [Качество и безопасность](#качество-и-безопасность)
6. [Внешние интеграции и API](#внешние-интеграции-и-api)
7. [Специфичные для команды практики](#специфичные-для-команды-практики)
8. [Антипаттерны и проблемные места](#антипаттерны-и-проблемные-места)
9. [Рекомендации для нового разработчика](#рекомендации-для-нового-разработчика)

---

## 1. Анализ стиля кодирования

### Именование
- Классы: CamelCase (`BaseDAO`, `Settings`, `S3Client`)
- Функции и переменные: snake_case (`find_one_or_none`, `get_articles`)
- Константы: UPPER_SNAKE_CASE (`MAX_PAGE_SIZE`)
- Файлы: snake_case, латиница (`router.py`, `dao.py`)
- Параметры: осмысленные, короткие (`user_id`, `category_id`)

**Пример:**
```python
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10 MB

def get_articles(...):
    ...
```

### Импорты и их организация
- Группировка: stdlib, third-party, first-party (isort, ruff)
- Порядок: PEP8, без wildcard

**Пример:**
```python
import math
import os
from fastapi import APIRouter, Depends
from app.articles.dao import ArticlesDAO
```

### Используемые code style стандарты
- PEP8 (flake8, ruff, black)
- Black: line-length=88, target-version=py311
- isort: profile=black
- flake8: кастомные игноры, exclude миграций
- ruff: основной линтер/форматтер

**Пример из .flake8:**
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503, B008, S101, S110, T201, E231
exclude = ...
```

### Документирование
- Docstrings для публичных функций, классов, методов
- Краткие, по делу, иногда с описанием параметров
- Комментарии: поясняющие, часто на русском

**Пример:**
```python
async def get_articles(...):
    """
    Получить все статьи с пагинацией и поиском
    """
    ...
```

---

## 2. Архитектурные паттерны

### Repository Pattern (DAO)
- BaseDAO реализует паттерн Repository/Data Access Object
- Все DAO-наследники определяют модель и используют общие методы

**Пример:**
```python
class UserDAO(BaseDAO):
    model = Users
user = await UserDAO.find_one_or_none(email="test@test.com")
```

### Service Layer
- Бизнес-логика вынесена в DAO и сервисы (например, S3Client, Celery-задачи)
- В роутерах вызываются методы DAO и сервисов

### Data Mapper
- SQLAlchemy 2.x (Declarative Mapping)

**Пример:**
```python
class Articles(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
```

### Singleton, Factory, DI
- settings = Settings(), logger = logging.getLogger() (Singleton)
- Depends(get_current_user) (DI FastAPI)

### Обработка ошибок
- try/except с логированием, HTTPException в роутерах

**Пример:**
```python
try:
    ...
except (SQLAlchemyError, Exception) as e:
    logger.error(...)
    return None
```

---

## 3. Структура и организация кода

### Модули и пакеты
- Строгое разделение по доменам: articles/, categories/, users/, services/, tasks/, core/, repo/
- Каждый домен: модели, DAO, роутеры, схемы
- Сервисы вынесены отдельно (например, S3Client)
- Тесты: unit/integration, фикстуры, мок-данные

**Пример:**
```
src/app/articles/
    dao.py
    models.py
    router.py
    schemas.py
src/app/services/
    s3_client.py
src/app/tasks/
    tasks.py
    celery_app.py
src/tests/
    unit_tests/
    integration_tests/
```

### Разделение ответственности
- DAO — только доступ к данным
- Сервисы — интеграция с внешними сервисами
- Роутеры — HTTP-логика, валидация, вызов бизнес-логики
- Конфиг — централизован через Pydantic BaseSettings
- Тесты — фикстуры, мок-данные, отдельные клиенты

**Пример фикстуры:**
```python
@pytest.fixture(scope="function")
async def ac():
    ...
```

---

## 4. Типизация и современные практики

### Type hints
- Используются повсеместно: модели, DAO, сервисы, роутеры
- SQLAlchemy 2.x: Mapped[Type], mapped_column
- Pydantic: схемы, конфиги

**Пример:**
```python
class Articles(Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
```

### Современный синтаксис
- Аннотации: str | None, list[...], Annotated
- Асинхронность: async/await
- Context manager: @asynccontextmanager
- F-строки

**Пример:**
```python
@asynccontextmanager
async def get_client(self):
    ...
```

---

## 5. Качество и безопасность

### Логирование
- logging + python-json-logger, формат JSON, уровень через LOG_LEVEL
- Логирование ошибок в DAO, сервисах, задачах Celery

**Пример:**
```python
logger = logging.getLogger()
logHandler = logging.StreamHandler()
formatter = CustomJsonFormatter(...)
logHandler.setFormatter(formatter)
logger.addHandler(logHandler)
logger.setLevel(settings.LOG_LEVEL)
```

### Валидация и работа с секретами
- Pydantic: для валидации входных данных, конфигов
- Пароли: bcrypt, проверка на стороне сервера
- Секреты: только через settings, .env не коммитится

**Пример:**
```python
class Settings(BaseSettings):
    SECRET_KEY: str
    ...
settings = Settings()
```

### Обработка ошибок
- Кастомные исключения от HTTPException
- Глобальный middleware для авторизации
- try/except с логированием

**Пример:**
```python
class UserAlreadyExistsException(BookingException):
    status_code = status.HTTP_409_CONFLICT
```

### Тестирование
- pytest, pytest-asyncio, фикстуры, мок-данные
- Покрытие: CRUD, права доступа, интеграция с внешними сервисами

---

## 6. Внешние интеграции и API

### API endpoints
- FastAPI, аннотированный стиль, docstrings, Pydantic-схемы
- Обработка ошибок через HTTPException

**Пример:**
```python
@router.get("/", response_model=ArticleListResponse)
async def get_articles(...):
    ...
```

### Внешние сервисы
- S3Client: отдельный сервис-класс, async context manager
- Celery: @celery.task, интеграция с email через SMTP

**Пример:**
```python
class S3Client:
    ...
    @asynccontextmanager
    async def get_client(self):
        ...
```

---

## 7. Специфичные для команды практики

### Кастомные утилиты
- Email templates: отдельный модуль для генерации email
- Конфиг: централизован через Pydantic BaseSettings
- Асинхронные клиенты для S3, БД, HTTP-клиентов в тестах

**Пример:**
```python
def create_register_confirmation_template(email_to: EmailStr):
    ...
```

### Внутренние соглашения
- Строгое разделение по слоям
- Асинхронность
- Использование Pydantic
- Миграции: Alembic, поддержка offline/online

### Работа с окружением
- MODE: DEV/TEST/PROD
- .env: все секреты и параметры окружения
- Settings: все параметры доступны через settings

---

## 8. Антипаттерны и проблемные места

### Нарушения SOLID
- В роутерах смешивается логика работы с файлами, валидация, бизнес-логика и обработка ошибок

### Дублирование кода
- Валидация изображений дублируется в create_article и update_article
- Обработка ошибок S3 дублируется

**Пример:**
```python
if image.content_type not in ALLOWED_IMAGE_TYPES:
    raise HTTPException(...)
```

### Устаревшие практики
- pass в except (лучше логировать)
- Комментарии на русском (для open source лучше английский)

### Сложные места без документации
- Логика soft delete, работа с S3

### Оптимизация
- Вынести повторяющийся код, всегда логировать ошибки, документировать сложные сценарии

---

## 9. Рекомендации для нового разработчика

- Соблюдать PEP8, использовать black, ruff, isort, pre-commit
- Следовать структуре: DAO — данные, сервисы — интеграции, роутеры — API
- Использовать type hints, Pydantic, асинхронность
- Все секреты — только через settings
- Для тестов использовать фикстуры, мок-данные, pytest-asyncio
- Не дублировать код, выносить повторяющиеся проверки в утилиты
- Логировать все ошибки, не использовать pass
- Документировать сложные места и бизнес-логику
- Примеры хорошего кода: BaseDAO, S3Client, Settings, фикстуры тестов
- Использовать pre-commit hooks, настраивать IDE на black/isort/ruff
- Code review: обращать внимание на типизацию, структуру, повторяемость, тесты, безопасность
