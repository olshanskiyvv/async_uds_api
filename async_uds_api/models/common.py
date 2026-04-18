from __future__ import annotations

from pydantic import Field

from async_uds_api.models.base import APIModel


class BranchInfo(APIModel):
    id: int = Field(description="Branch ID in the UDS.")
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
        description="Branch name.",
    )


class ParticipantShortInfo(APIModel):
    id: int = Field(description="Customer ID in the company.")
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
        description="Customer name.",
    )
