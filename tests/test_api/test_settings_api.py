import pytest
import respx
from httpx import Response

from async_uds_api.models import CompanySettings
from tests.fixtures.api_responses import COMPANY_SETTINGS_RESPONSE


@pytest.mark.asyncio
class TestSettingsAPI:
    async def test_get_settings_success(self, uds_client):
        """Test successful settings retrieval."""
        respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=Response(200, json=COMPANY_SETTINGS_RESPONSE)
        )

        result = await uds_client.settings.get()

        assert isinstance(result, CompanySettings)
        assert result.id == 123456
        assert result.name == "Test Company"

    @pytest.mark.asyncio
    async def test_get_settings_401_error(self, uds_client):
        """Test settings retrieval with 401 error."""
        from async_uds_api import UDSUnauthorizedError

        respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=Response(401, json={"message": "Unauthorized"})
        )

        with pytest.raises(UDSUnauthorizedError):
            await uds_client.settings.get()

    @pytest.mark.asyncio
    async def test_get_settings_404_error(self, uds_client):
        """Test settings retrieval with 404 error."""
        from async_uds_api import UDSNotFoundError

        respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=Response(404, json={"message": "Not found"})
        )

        with pytest.raises(UDSNotFoundError):
            await uds_client.settings.get()
