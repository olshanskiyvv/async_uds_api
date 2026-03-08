from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field


class TagModel(BaseModel):
    id: int = Field(description="Tag identifier.")
    name: str = Field(description="Tag name.")


class TagsPage(BaseModel):
    rows: List[TagModel] = Field(default_factory=list, description="List of tags.")
    total: int = Field(default=0, description="Tags total count.")
