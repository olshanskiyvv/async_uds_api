import time
from typing import TYPE_CHECKING

from async_uds_api.models import CompanySettings

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class SettingsAPI:
    def __init__(self, client: "UDSClient", ttl: float = 60.0) -> None:
        self._client = client
        self._ttl = ttl
        self._cached: CompanySettings | None = None
        self._cached_at: float = 0.0

    async def get(self) -> CompanySettings:
        """Return company settings, served from cache within the TTL window."""
        now = time.monotonic()
        if self._cached is not None and now - self._cached_at < self._ttl:
            return self._cached
        data = await self._client._get_json("/settings")
        self._cached = CompanySettings.model_validate(data)
        self._cached_at = now
        return self._cached

    def invalidate(self) -> None:
        """Clear the cached settings, forcing a fresh fetch on next call."""
        self._cached = None
        self._cached_at = 0.0
