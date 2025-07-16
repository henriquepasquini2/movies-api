from typing import List, Optional

from fastapi import Query
from pydantic import computed_field

from models.base import BaseAPIModel


class BaseRequest(BaseAPIModel):
    """Base params."""

    fields: Optional[str] = Query(
        default="",
        description="List of fields to be returned in the response (comma separated)",
    )
    page: Optional[int] = Query(default=1, description="Page number")
    size: Optional[int] = Query(
        default=10000,
        description="Number of records to be returned in the response",
    )

    @computed_field(return_type=List[str])
    def fields_list(self) -> List[str]:
        if self.fields is None or self.fields.strip() == "":
            return []
        return list(set(self.fields.strip().replace(" ", "").split(",")))
