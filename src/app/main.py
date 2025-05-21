from fastapi import FastAPI
from app.api.routers import articles, categories

app = FastAPI()

app.include_router(articles.router)
app.include_router(categories.router)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(
    name: str,
):
    return {"message": f"Hello {name}"}
