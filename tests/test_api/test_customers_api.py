import pytest
import respx
from httpx import Response

from async_uds_api.models import CustomerDetail, CustomersPage, TagsPage
from tests.fixtures.api_responses import (
    CUSTOMER_DETAIL_RESPONSE,
    CUSTOMER_TAGS_RESPONSE,
    CUSTOMERS_LIST_RESPONSE,
)


@pytest.mark.asyncio
class TestCustomersAPI:
    async def test_list_customers_success(self, uds_client):
        """Test successful customers list retrieval."""
        respx.get("https://api.uds.app/partner/v2/customers").mock(
            return_value=Response(200, json=CUSTOMERS_LIST_RESPONSE)
        )

        result = await uds_client.customers.list()

        assert isinstance(result, CustomersPage)
        assert len(result.rows) == 2
        assert result.rows[0].uid == "abc123"

    async def test_list_customers_with_pagination(self, uds_client):
        """Test customers list with pagination parameters."""
        respx.get(
            "https://api.uds.app/partner/v2/customers",
            params={"max": "10", "offset": "20"},
        ).mock(return_value=Response(200, json=CUSTOMERS_LIST_RESPONSE))

        result = await uds_client.customers.list(max=10, offset=20)

        assert isinstance(result, CustomersPage)

    async def test_get_customer_success(self, uds_client):
        """Test successful customer retrieval by ID."""
        customer_id = 123

        respx.get(
            f"https://api.uds.app/partner/v2/customers/{customer_id}"
        ).mock(return_value=Response(200, json=CUSTOMER_DETAIL_RESPONSE))

        result = await uds_client.customers.get(customer_id)

        assert isinstance(result, CustomerDetail)
        assert result.uid == "abc123"
        assert len(result.tags) == 2

    async def test_get_customer_tags(self, uds_client):
        """Test getting customer tags."""
        customer_id = 123

        respx.get(
            f"https://api.uds.app/partner/v2/customers/{customer_id}/tags"
        ).mock(return_value=Response(200, json=CUSTOMER_TAGS_RESPONSE))

        result = await uds_client.customers.get_tags(customer_id)

        assert isinstance(result, TagsPage)
        assert result.total == 2
        assert len(result.rows) == 2

    async def test_set_customer_tags(self, uds_client):
        """Test setting customer tags."""
        customer_id = 123
        tag_ids = [1, 2, 3]

        respx.post(
            f"https://api.uds.app/partner/v2/customers/{customer_id}/tags"
        ).mock(return_value=Response(200, json=CUSTOMER_TAGS_RESPONSE))

        result = await uds_client.customers.set_tags(customer_id, tag_ids)

        assert isinstance(result, TagsPage)

    async def test_find_customer_by_phone(self, uds_client):
        """Test finding customer by phone."""
        from async_uds_api.models import PurchaseCalcResponse

        respx.get(
            "https://api.uds.app/partner/v2/customers/find",
            params={"phone": "+79001234567"},
        ).mock(
            return_value=Response(
                200,
                json={
                    "user": CUSTOMER_DETAIL_RESPONSE,
                    "purchase": {},
                },
            )
        )

        result = await uds_client.customers.find(phone="+79001234567")

        assert isinstance(result, PurchaseCalcResponse)

    async def test_customer_not_found(self, uds_client):
        """Test customer not found error."""
        from async_uds_api import UDSNotFoundError

        customer_id = 999999

        respx.get(
            f"https://api.uds.app/partner/v2/customers/{customer_id}"
        ).mock(return_value=Response(404, json={"message": "Not found"}))

        with pytest.raises(UDSNotFoundError):
            await uds_client.customers.get(customer_id)
