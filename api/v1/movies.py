from typing import List

from fastapi import APIRouter, Depends

from schemas.requests.base import BaseRequest
from schemas.requests.movies import SearchMoviesRequest
from schemas.responses.movies import MoviesResponse
from services.movies import MoviesService
from utils.decorators import cached

router = APIRouter()

movies_service = MoviesService()

@router.get(
    path="", description="List movies in the database. This endpoint is paginated."
)
@cached(expiration_seconds=3600)
async def list_movies(
    request: BaseRequest = Depends(),
    service: MoviesService = Depends(lambda: movies_service),
):
    movies = await service.get_all_movies(request)
    return movies

@router.post(
    "/titles",
    description="Search movies based on the title requested.",
)
@cached(expiration_seconds=3600)
async def search_movies_by_titles(
    request: SearchMoviesRequest,
    service: MoviesService = Depends(lambda: movies_service),
):
    movies = await service.search_movies(request)
    return movies

@router.get("/{id}", response_model=List[MoviesResponse])
async def fetch_movie_by_id(
    id: str,
    service: MoviesService = Depends(lambda: movies_service),
):
    # Implement this
    movies = await service.filter_movies(id)
    return movies

@router.get("/{title}", response_model=List[MoviesResponse])
async def fetch_movie_by_title(
    title: str,
    service: MoviesService = Depends(lambda: movies_service),  # Dependency injection
):
    # Implement this
    movies = await service.filter_movies(title)
    return movies 