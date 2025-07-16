from fastapi import APIRouter

from api.v1.movies import router as movies_router

api_router = APIRouter()
api_router.include_router(movies_router, prefix="/movies", tags=["movies"])
