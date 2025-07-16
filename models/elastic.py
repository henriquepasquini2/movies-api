from typing import Any, Dict, List, Optional

from pydantic import Field

from models.base import BaseAPIModel


class ESBaseRequest(BaseAPIModel):
    index: str
    body: Dict[str, Any] = Field(..., description="Elasticsearch query DSL.")
    size: Optional[int] = Field(
        default=10, ge=1, le=10000, description="Number of results to fetch."
    )
    scroll: Optional[str] = Field(default="5m")
    request_timeout: Optional[int] = Field(
        120, description="Time each individual request should wait for responses."
    )


class ESSearchRequest(ESBaseRequest):
    """Defines a search command to send to Elasticsearch."""

    from_: Optional[int] = Field(
        0, ge=0, description="Simple pagination offset from which to fetch results."
    )


class ElasticsearchResponse(BaseAPIModel):
    """Response model for Elasticsearch queries."""

    hits: List[Dict[str, Any]] = Field(
        ..., description="List of hits returned by Elasticsearch."
    )
    total: int = Field(..., description="Total number of results found.")
