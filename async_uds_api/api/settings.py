from typing import TYPE_CHECKING

from ..models import CompanySettings

if TYPE_CHECKING:
    from ..client import UDSClient


class SettingsAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def get(self) -> CompanySettings:
        data = await self._client._get_json("/settings")
        return CompanySettings.model_validate(data)
