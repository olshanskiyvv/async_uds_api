import pytest
import respx
from httpx import Response

from async_uds_api import UDSClient
from async_uds_api.models import CompanySettings
from tests.fixtures.settings import COMPANY_SETTINGS_RESPONSE


class TestSettingsAPI:
    async def test_get_settings_success(self, uds_client):
        respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=Response(200, json=COMPANY_SETTINGS_RESPONSE)
        )

        result = await uds_client.settings.get()

        assert isinstance(result, CompanySettings)
        assert result.id == 123456
        assert result.name == "Test Company"

    async def test_get_settings_401_error(self, uds_client):
        from async_uds_api import UDSUnauthorizedError

        respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=Response(401, json={"message": "Unauthorized"})
        )

        with pytest.raises(UDSUnauthorizedError):
            await uds_client.settings.get()

    async def test_get_settings_404_error(self, uds_client):
        from async_uds_api import UDSNotFoundError

        respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=Response(404, json={"message": "Not found"})
        )

        with pytest.raises(UDSNotFoundError):
            await uds_client.settings.get()

    async def test_cache_hit_within_ttl(self, mock_httpx):
        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            settings_ttl=60.0,
        ) as client:
            route = respx.get("https://api.uds.app/partner/v2/settings").mock(
                return_value=Response(200, json=COMPANY_SETTINGS_RESPONSE)
            )

            first = await client.settings.get()
            second = await client.settings.get()

            assert first is second
            assert route.call_count == 1

    async def test_cache_miss_after_ttl(self, mock_httpx):
        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            settings_ttl=30.0,
        ) as client:
            route = respx.get("https://api.uds.app/partner/v2/settings").mock(
                return_value=Response(200, json=COMPANY_SETTINGS_RESPONSE)
            )

            await client.settings.get()
            client.settings._cached_at = 0.0
            await client.settings.get()

            assert route.call_count == 2

    async def test_invalidate_clears_cache(self, mock_httpx):
        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            settings_ttl=60.0,
        ) as client:
            route = respx.get("https://api.uds.app/partner/v2/settings").mock(
                return_value=Response(200, json=COMPANY_SETTINGS_RESPONSE)
            )

            await client.settings.get()
            client.settings.invalidate()
            await client.settings.get()

            assert route.call_count == 2
