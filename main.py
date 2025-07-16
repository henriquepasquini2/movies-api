from contextlib import asynccontextmanager

from fastapi import FastAPI

from api import api_router
from config import settings
from connections.elastic import Elasticsearch
from connections.redis_manager import RedisManager


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    cache = RedisManager()
    cache.initialize()
    elastic = Elasticsearch()
    await elastic.initialize()

    yield

    # Cleanup resources
    cache.close()
    await elastic.close()


app = FastAPI(
    title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, lifespan=lifespan
)

app.include_router(api_router)


@app.get("/")
async def root():
    return {"message": "Welcome to the Movie Database API"}
