from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class APIModel(BaseModel):
    """Base model class with common configuration for all API models."""

    model_config = ConfigDict(
        populate_by_name=True,
        alias_generator=to_camel,
    )
