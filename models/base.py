from pydantic import BaseModel


class BaseAPIModel(BaseModel):

    class Config:
        """
        Base class configuration for all Pydantic models. This class can be used
        to centralize common configurations for Pydantic models, such as ORM support,
        alias generation, etc.
        """

        # Forbid extra attributes in Pydantic models
        extra = "forbid"
        # Enables ORM mode for Pydantic models (useful when working with ORMs like SQLAlchemy)
        from_attributes = True
        # Strip whitespace from all string values
        str_strip_whitespace = True
