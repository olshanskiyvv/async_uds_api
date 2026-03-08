from typing import TYPE_CHECKING

from ..models import TagsPage

if TYPE_CHECKING:
    from ..client import UDSClient


class TagsAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def list(self) -> TagsPage:
        data = await self._client._get_json("/tags")
        return TagsPage.model_validate(data)
