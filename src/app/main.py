from fastapi import FastAPI
from app.articles.router import router as router_articles
from app.categories.router import router as router_categories

app = FastAPI()

app.include_router(router_articles)
app.include_router(router_categories)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(
    name: str,
):
    return {"message": f"Hello {name}"}
