from pydantic import BaseModel, ConfigDict


class APIModel(BaseModel):
    """Base model class with common configuration for all API models."""

    model_config = ConfigDict(populate_by_name=True)
