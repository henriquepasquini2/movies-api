from typing import List

from fastapi import HTTPException
from pydantic import ValidationError

from constants.index import Index
from models.elastic import ESBaseRequest
from schemas.requests.base import BaseRequest
from schemas.requests.movies import SearchMoviesRequest
from schemas.responses.movies import MoviesCountPerGenreResponse, MoviesResponse
from services.base import BaseService
from utils.elastic_query import build_query_movie

class MoviesService(BaseService):
    def __init__(self):
        super().__init__()
        self.index = Index.movie

    async def get_all_movies(self, request: BaseRequest) -> List[dict]:
        """Get all movies from the Elasticsearch index."""
        query = {"query": {"match_all": {}}}
        result = await self.search(query, request)
        return result

    async def search_movies(
        self, request: SearchMoviesRequest
    ) -> List[MoviesCountPerGenreResponse]:
        body = {"query": build_query_movie(request), "_source": ["title_normalized"]}
        result = await self.search(body, request)
        return result

    async def search(
        self,
        body: dict,
        params: SearchMoviesRequest,
        scroll: str = "1m",
    ):
        elastic_request = ESBaseRequest(
            index=self.index, body=body, size=params.size, scroll=scroll
        )
        movies = await self.es.search_async_scan(elastic_request)
        filtered_fields = self._filter_fields(movies, body.get("_source"))
        result = self._build_response(filtered_fields)
        return result

    def _build_response(self, filtered_fields):
        result = []
        for field in filtered_fields:
            response = MoviesResponse(**field)
            result.append(response.model_dump())
        return result

    def _filter_fields(self, movies, fields):
        try:
            filtered = []
            for movie in movies.hits:
                response = MoviesResponse(**movie["_source"])
                self._invalidate_unknown_fields(response, fields)
                filtered_data = (
                    response.model_dump(include=fields)
                    if fields
                    else response.model_dump()
                )
                filtered.append(filtered_data)
            return filtered
        except ValidationError as e:
            raise HTTPException(
                status_code=500, detail=f"Error validating search movies response: {e}"
            )

    @staticmethod
    def _invalidate_unknown_fields(response, fields):
        fields_set = set(fields) if fields else None
        if fields_set and not fields_set.issubset(set(response.dict().keys())):
            raise HTTPException(
                status_code=400,
                detail=f"Unknown fields: {fields_set.difference(response.dict().keys())}",
            )

    async def filter_movies(self, value: str):
        try:
            # Try to interpret as integer ID
            query = {"query": {"term": {"id": int(value)}}}
        except ValueError:
            # Try exact normalized title
            normalized_title = value.lower()
            query = {"query": {"term": {"title_normalized": normalized_title}}}
        request = ESBaseRequest(
            index=self.index, body=query, size=10, scroll="1m"
        )
        movies = await self.es.search_async_scan(request)
        filtered_fields = self._filter_fields(movies, None)
        result = self._build_response(filtered_fields)
        # Fallback to match if no results and not an ID search
        if not result and not value.isdigit():
            query = {"query": {"match": {"title": value}}}
            request = ESBaseRequest(
                index=self.index, body=query, size=10, scroll="1m"
            )
            movies = await self.es.search_async_scan(request)
            filtered_fields = self._filter_fields(movies, None)
            result = self._build_response(filtered_fields)
        return result 