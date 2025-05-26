# Market Blog API

Полнофункциональное REST API для управления блогом с системой аутентификации, категориями статей и асинхронной обработкой задач.

## 🚀 Особенности

- **Аутентификация и авторизация** с JWT токенами
- **Асинхронная отправка email** через Celery и Redis
- **Полнотекстовый поиск** по статьям (PostgreSQL)
- **Постраничная пагинация** с настраиваемыми параметрами
- **Загрузка изображений** в S3-совместимое хранилище
- **Soft delete** для статей
- **Middleware** для проверки авторизации
- **Категории** для организации контента

## 🛠 Технологический стек

### Backend
- **Python 3.13** - основной язык
- **FastAPI** - веб-фреймворк
- **PostgreSQL** - основная база данных
- **Redis** - кэш и брокер сообщений
- **Celery** - асинхронные задачи
- **Alembic** - миграции БД

### Инфраструктура
- **Docker & Docker Compose** - контейнеризация
- **uv** - управление пакетами
- **Gunicorn + Uvicorn** - ASGI сервер

### Дополнительные инструменты
- **Pydantic** - валидация данных
- **SQLAlchemy** - ORM
- **S3 Storage** - хранение файлов
- **JWT** - токены аутентификации

## 📋 API Endpoints

### 🔐 Аутентификация
- `POST /auth/register` - Регистрация пользователя
- `POST /auth/login` - Авторизация
- `POST /auth/logout` - Выход из системы

### 📝 Статьи
- `GET /articles` - Список статей (с поиском, фильтрацией, пагинацией)
- `POST /articles` - Создание статьи
- `GET /articles/{id}` - Получение статьи
- `PUT /articles/{id}` - Обновление статьи
- `DELETE /articles/{id}` - Удаление статьи (soft delete)

### 🏷 Категории
- `GET /categories` - Список категорий
- `POST /categories` - Создание категории

### Query параметры для статей:
- `search` - полнотекстовый поиск
- `category_id` - фильтр по категории
- `page_number` - номер страницы
- `page_size` - размер страницы (макс. 100)

## 🚀 Быстрый старт

### Предварительные требования
- Docker и Docker Compose
- Python 3.13+ (для локальной разработки)

### 1. Клонирование репозитория
```bash
git clone <repository-url>
cd soter_market
```

### 2. Настройка переменных окружения
```bash
cp .env-example .env-non-dev
# Отредактируйте .env-non-dev под ваши настройки
```

### 3. Запуск с Docker Compose
```bash
# Сборка и запуск всех сервисов
docker-compose up --build

# В фоновом режиме
docker-compose up -d --build
```

### 4. Проверка работоспособности
- API: http://localhost:7777
- Swagger UI: http://localhost:7777/docs
- ReDoc: http://localhost:7777/redoc

## 🔧 Локальная разработка

### Настройка окружения
```bash
# Установка uv (если не установлен)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установка зависимостей
uv install

# Активация виртуального окружения
source .venv/bin/activate  # Linux/Mac
# или
.venv\Scripts\activate     # Windows
```

### Настройка IDE (PyCharm)
1. Правый клик на папку `src` → Mark Directory as → Sources Root
2. File → Settings → Project → Python Interpreter → выберите `.venv/bin/python`

### Запуск для разработки
```bash
cd src
fastapi dev app/main.py
```

### Запуск миграций
```bash
cd src
alembic upgrade head
```

## 🐳 Docker команды

```bash
# Просмотр логов
docker-compose logs -f

# Просмотр логов конкретного сервиса
docker-compose logs -f market
docker-compose logs -f celery

# Перезапуск сервисов
docker-compose restart

# Остановка
docker-compose down

# Остановка с удалением volumes
docker-compose down -v

# Пересборка конкретного сервиса
docker-compose build market
```


## 🔐 Переменные окружения

Основные переменные в `.env-non-dev`:

```env
# Режим работы
MODE=DEV

# База данных
DB_HOST=db
DB_PORT=5432
DB_USER=postgres
DB_PASS=postgres
DB_NAME=market_app

# Redis
REDIS_HOST=market_redis
REDIS_PORT=6379

# JWT
SECRET_KEY=your-secret-key
ALGORITHM=HS256

# Email
SMTP_HOST=smtp.gmail.com
SMTP_PORT=465
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# S3 Storage
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://s3.ru-7.storage.selcloud.ru
S3_BUCKET_NAME=your-bucket-name
```

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

```

## 📚 Документация API

После запуска приложения документация доступна по адресам:
- **Swagger UI**: http://localhost:7777/docs
- **ReDoc**: http://localhost:7777/redoc

## 🔍 Основные возможности

### Аутентификация
- Регистрация с подтверждением по email
- JWT токены в HTTP-only cookies
- Middleware для проверки авторизации

### Статьи
- Создание с загрузкой изображений
- Полнотекстовый поиск по содержимому
- Фильтрация по категориям
- Постраничная пагинация
- Soft delete

### Асинхронные задачи
- Отправка email уведомлений
- Celery с Redis как брокер
- Celery Beat для периодических задач

## 🤝 Разработка

### Pre-commit hooks
```bash
pre-commit install
pre-commit run --all-files
```

### Линтинг и форматирование
```bash
ruff check .
ruff format .
```
