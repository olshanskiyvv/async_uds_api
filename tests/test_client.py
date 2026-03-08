import httpx
import pytest

from async_uds_api import UDSClient


class TestUDSClient:
    def test_client_initialization(self):
        """Test UDSClient initialization."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
        )

        assert client._company_id == 123456
        assert client._api_key == "test-api-key"
        assert client._base_url == "https://api.uds.app/partner/v2"

    def test_client_default_values(self):
        """Test UDSClient default values."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
        )

        assert client._timeout == 10.0
        assert client._external_client is False

    def test_client_custom_base_url(self):
        """Test UDSClient with custom base URL."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
            base_url="https://custom.api.com/v1",
        )

        assert client._base_url == "https://custom.api.com/v1"

    def test_client_custom_timeout(self):
        """Test UDSClient with custom timeout."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
            timeout=30.0,
        )

        assert client._timeout == 30.0

    @pytest.mark.asyncio
    async def test_client_context_manager(self):
        """Test UDSClient as async context manager."""
        async with UDSClient(
            company_id=123456,
            api_key="test-api-key",
        ) as client:
            assert client is not None
            assert isinstance(client, UDSClient)

    def test_client_build_headers(self):
        """Test UDSClient header generation."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
        )

        headers = client._build_headers()

        assert "Accept" in headers
        assert headers["Accept"] == "application/json"
        assert "X-Origin-Request-Id" in headers
        assert "X-Timestamp" in headers

    def test_client_build_auth(self):
        """Test UDSClient basic auth generation."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
        )

        auth = client._build_auth()

        assert isinstance(auth, httpx.BasicAuth)

    def test_client_api_attributes(self):
        """Test UDSClient has all API attributes."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
        )

        assert hasattr(client, "settings")
        assert hasattr(client, "customers")
        assert hasattr(client, "operations")
        assert hasattr(client, "tags")
        assert hasattr(client, "goods")
        assert hasattr(client, "images")

    @pytest.mark.asyncio
    async def test_client_close(self):
        """Test UDSClient close method."""
        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
        )

        await client.aclose()

    @pytest.mark.asyncio
    async def test_client_with_external_httpx_client(self):
        """Test UDSClient with external httpx.AsyncClient."""
        external_client = httpx.AsyncClient(
            base_url="https://api.uds.app/partner/v2",
        )

        client = UDSClient(
            company_id=123456,
            api_key="test-api-key",
            client=external_client,
        )

        assert client._external_client is True

        await client.aclose()
        await external_client.aclose()
