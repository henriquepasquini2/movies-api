from fastapi import APIRouter, Depends

from api.v1 import api_router as v1_router
from connections.redis_manager import RedisManager

api_router = APIRouter()
api_router.include_router(v1_router, prefix="/v1")

redis_manager = RedisManager()


@api_router.get("/healthcheck")
async def healthcheck():
    return {"status": "ok"}


@api_router.post(
    "/cache/delete",
    responses={
        404: {"description": "{key} not found"},
        200: {"description": "{key} deleted from cache"},
    },
)
async def delete_cache_key(
    key: str,
    cache: RedisManager = Depends(lambda: redis_manager),
):
    await cache.delete(key)
    return {"description": f"{key} deleted from cache"}
