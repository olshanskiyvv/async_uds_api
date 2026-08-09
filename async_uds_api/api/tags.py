from typing import TYPE_CHECKING

from async_uds_api.models import TagsPage

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class TagsAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def list(self, *, request_id: str | None = None) -> TagsPage:
        """Return all tags defined for the company."""
        data = await self._client._get_json("/tags", request_id=request_id)
        return TagsPage.model_validate(data)
