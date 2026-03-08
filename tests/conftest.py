import pytest
import respx

from async_uds_api import UDSClient


@pytest.fixture
def mock_httpx():
    """Mock HTTP client with respx."""
    with respx.mock:
        yield


@pytest.fixture
async def uds_client(mock_httpx):
    """Create UDSClient instance for testing."""
    async with UDSClient(
        company_id=123456,
        api_key="test-api-key",
    ) as client:
        yield client
