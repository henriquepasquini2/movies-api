from typing import List, Optional

from pydantic import Field, field_validator, model_validator

from schemas.requests.base import BaseAPIModel
from utils import string_utils


class SearchMoviesRequest(BaseAPIModel):
    size: Optional[int] = Field(
        default=1000,
        description="Number of movies to be searched in the async scan.",
    )
    titles: List[str] = Field(
        [],
        title="Titles",
        description="List of movie titles to search for.",
        examples=[["The Godfather", "Inception"]],
    )
    exact_match: bool = Field(
        False, description="If True, search 'titles' with exact match."
    )
    keep_order_span: bool = Field(
        True, description="If True, search 'titles' with all words in order."
    )
    fuzziness: str = Field(
        "AUTO:1,8", description="Fuzziness value for searching the 'titles' list."
    )
    slop: int = Field(1, description="Slop value for searching the 'titles' list.")
    n_titles: List[str] = Field(
        [],
        title="Negative Titles",
        description="Titles to **exclude** from the search.",
        examples=[["The Room"]],
    )
    n_titles_exact_match: bool = Field(
        False, description="If True, search 'n_titles' with exact match."
    )
    n_titles_keep_order_span: bool = Field(
        True, description="Search 'n_titles' with all words in order."
    )
    n_titles_fuzziness: str = Field(
        "AUTO:1,8",
        description="Fuzziness value for searching the 'n_titles' list.",
    )
    n_titles_slop: int = Field(
        1, description="Slop value for searching the 'n_titles' list."
    )
    @staticmethod
    @field_validator("fuzziness", mode="before")
    def validate_fuzziness(value):
        if isinstance(value, int):
            value = str(value)
        return value
    @model_validator(mode="after")
    def validate_titles(cls, values):
        if values.titles:
            titles = []
            for title in values.titles:
                if values.exact_match:
                    title = title.lower()
                else:
                    title = string_utils.normalized_text(title).lower()
                if title:
                    titles.append(title)
            values.titles = titles
        if values.n_titles:
            n_titles = []
            for n_title in values.n_titles:
                if values.n_titles_exact_match:
                    n_title = n_title.lower()
                else:
                    n_title = string_utils.normalized_text(n_title).lower()
                if n_title:
                    n_titles.append(n_title)
            values.n_titles = n_titles
        return values
