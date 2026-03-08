from __future__ import annotations

from pydantic import BaseModel, Field


class BranchInfo(BaseModel):
    id: int = Field(description="Branch ID in the UDS.")
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
        description="Branch name.",
    )
