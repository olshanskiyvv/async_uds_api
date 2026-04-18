from __future__ import annotations

from pydantic import Field

from async_uds_api.models.base import APIModel


class TagModel(APIModel):
    id: int = Field(description="Tag identifier.")
    name: str = Field(description="Tag name.")


class TagsPage(APIModel):
    rows: list[TagModel] = Field(
        default_factory=list, description="List of tags."
    )
    total: int = Field(default=0, description="Tags total count.")
