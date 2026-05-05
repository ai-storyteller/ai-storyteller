from pydantic import BaseModel as PydanticBaseModel
from pydantic import ConfigDict, alias_generators

__all__ = ("BaseModel",)


class BaseModel(PydanticBaseModel):
    """
    Base model for all requests.

    This handles the conversion of snake_case to camelCase.
    """

    model_config = ConfigDict(
        alias_generator=alias_generators.to_camel,
        populate_by_name=True,
    )
