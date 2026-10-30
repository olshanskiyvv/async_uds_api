from __future__ import annotations

from pydantic import Field

from async_uds_api.models.base import APIModel


class BranchInfo(APIModel):
    """Company branch information."""

    id: int = Field(description="Branch ID in the UDS.")
    display_name: str = Field(
        description="Branch name.",
    )


class ParticipantShortInfo(APIModel):
    """Short information about a loyalty program participant."""

    id: int = Field(description="Customer ID in the company.")
    display_name: str = Field(
        description="Customer name.",
    )
