from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.articles.router import router as router_articles
from app.categories.router import router as router_categories
from app.users.router import router_users, router_auth
from app.users.dependencies import get_current_user, get_token
from app.exceptions import (
    TokenAbsentException,
    TokenExpiredException,
    IncorrectTokenFormatException,
    UserIsNotPresentException,
)

app = FastAPI()

# Подключение CORS, чтобы запросы к API могли приходить из браузера
origins = [
    # 3000 - порт, на котором работает фронтенд на React.js
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS", "DELETE", "PATCH", "PUT"],
    allow_headers=[
        "Content-Type",
        "Set-Cookie",
        "Access-Control-Allow-Headers",
        "Access-Control-Allow-Origin",
        "Authorization",
    ],
)

# Эндпоинты, которые не требуют аутентификации
EXCLUDED_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/login",
    "/auth/register",
    "/",
    "/hello",
}


def _is_excluded_path(path: str) -> bool:
    """Проверяет, исключен ли путь из аутентификации"""
    if path in EXCLUDED_PATHS:
        return True

    excluded_prefixes = ["/docs", "/redoc", "/static", "/auth", "/hello"]
    for prefix in excluded_prefixes:
        if path.startswith(prefix):
            return True
    return False


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    # Проверяем, нужна ли аутентификация для данного пути
    if _is_excluded_path(request.url.path):
        return await call_next(request)

    try:
        # Пытаемся получить и проверить токен
        token = get_token(request)
        user = await get_current_user(token)

        # Добавляем пользователя в state запроса для дальнейшего использования
        request.state.current_user = user

    except (
        TokenAbsentException,
        TokenExpiredException,
        IncorrectTokenFormatException,
        UserIsNotPresentException,
    ) as e:
        return JSONResponse(status_code=401, content={"detail": str(e)})
    except Exception:
        return JSONResponse(
            status_code=500,
            content={"detail": "Внутренняя ошибка сервера"},
        )

    response = await call_next(request)
    return response


# Подключаем роутеры
app.include_router(router_auth)
app.include_router(router_users)
app.include_router(router_articles)
app.include_router(router_categories)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}
