from typing import Generic, List, TypeVar

from models.base import BaseAPIModel

T = TypeVar("T")


class BaseResponse(BaseAPIModel):
    """Base payload for all requests."""


class PaginatedResponse(BaseResponse, Generic[T]):
    items: List[T]
    total: int
    page: int
    page_size: int
    total_pages: int
