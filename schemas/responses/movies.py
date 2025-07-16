from typing import Optional

from pydantic import Field

from schemas.responses.base import BaseResponse


class MoviesResponse(BaseResponse):
    id: Optional[int] = Field(
        None,
        title="Movie ID",
        description="ID of the movie in the database.",
        examples=["123"],
    )
    imdb_id: Optional[str] = Field(
        None,
        title="IMDB ID",
        description="IMDB ID of the movie.",
        examples=["tt0111161"],
    )
    title: Optional[str] = Field(
        None,
        title="Title",
        description="Title of the movie.",
        examples=["The Shawshank Redemption"],
    )
    title_normalized: Optional[str] = Field(
        None,
        title="Normalized Title",
        description="Normalized title of the movie.",
        examples=["shawshank redemption"],
    )
    release_year: Optional[int] = Field(
        None,
        title="Release Year",
        description="Year the movie was released.",
        examples=[1994],
    )
    genre: Optional[str] = Field(
        None,
        title="Genre",
        description="Genre of the movie.",
        examples=["Drama"],
    )
    director: Optional[str] = Field(
        None,
        title="Director",
        description="Director of the movie.",
        examples=["Frank Darabont"],
    )
    additional_data: Optional[dict | list] = Field(
        None,
        title="Additional Data",
        description="Additional data about the movie.",
        examples=[{"key": "value"}],
    )

class MoviesCountPerGenreResponse(BaseResponse):
    genre: Optional[str] = Field(
        None,
        title="Genre",
        description="Genre of the movie.",
        examples=["Drama"],
    )
    doc_count: Optional[int] = Field(
        0,
        title="Document Count",
        description="Number of movies found for each genre.",
        examples=[0],
    )
