import pytest
import respx
from httpx import Response

from async_uds_api.models import (
    GoodsDetailed,
    GoodsItemType,
    GoodsPage,
    GoodsType,
)
from tests.fixtures.api_responses import (
    GOODS_DETAIL_RESPONSE,
    GOODS_LIST_RESPONSE,
)


@pytest.mark.asyncio
class TestGoodsAPI:
    async def test_list_goods_success(self, uds_client):
        """Test successful goods list retrieval."""
        respx.get("https://api.uds.app/partner/v2/goods").mock(
            return_value=Response(200, json=GOODS_LIST_RESPONSE)
        )

        result = await uds_client.goods.list()

        assert isinstance(result, GoodsPage)
        assert result.total == 1
        assert len(result.rows) == 1

    async def test_list_goods_with_filters(self, uds_client):
        """Test goods list with filters."""
        respx.get(
            "https://api.uds.app/partner/v2/goods",
            params={"nodeId": "123"},
        ).mock(return_value=Response(200, json=GOODS_LIST_RESPONSE))

        result = await uds_client.goods.list(node_id=123)

        assert isinstance(result, GoodsPage)

    async def test_create_goods_item(self, uds_client):
        """Test creating goods item."""
        goods = GoodsDetailed(
            name="Test Item",
            data=GoodsItemType(
                type=GoodsType.ITEM,
                price=100.0,
            ),
        )

        respx.post("https://api.uds.app/partner/v2/goods").mock(
            return_value=Response(200, json=GOODS_DETAIL_RESPONSE)
        )

        result = await uds_client.goods.create(goods)

        assert isinstance(result, GoodsDetailed)

    async def test_get_goods_success(self, uds_client):
        """Test successful goods retrieval by ID."""
        goods_id = 1

        respx.get(f"https://api.uds.app/partner/v2/goods/{goods_id}").mock(
            return_value=Response(200, json=GOODS_DETAIL_RESPONSE)
        )

        result = await uds_client.goods.get(goods_id)

        assert isinstance(result, GoodsDetailed)
        assert result.id == 1

    async def test_update_goods_success(self, uds_client):
        """Test successful goods update."""
        goods_id = 1
        goods = GoodsDetailed(
            name="Updated Item",
            data=GoodsItemType(
                type=GoodsType.ITEM,
                price=150.0,
            ),
        )

        respx.put(f"https://api.uds.app/partner/v2/goods/{goods_id}").mock(
            return_value=Response(200, json=GOODS_DETAIL_RESPONSE)
        )

        result = await uds_client.goods.update(goods_id, goods)

        assert isinstance(result, GoodsDetailed)

    async def test_delete_goods_success(self, uds_client):
        """Test successful goods deletion."""
        goods_id = 1

        respx.delete(f"https://api.uds.app/partner/v2/goods/{goods_id}").mock(
            return_value=Response(204)
        )

        await uds_client.goods.delete(goods_id)

    async def test_get_goods_by_external_id(self, uds_client):
        """Test getting goods by external ID."""
        external_id = "external-123"

        respx.get(
            f"https://api.uds.app/partner/v2/goods/external/{external_id}"
        ).mock(return_value=Response(200, json=GOODS_DETAIL_RESPONSE))

        result = await uds_client.goods.external.get(external_id)

        assert isinstance(result, GoodsDetailed)

    async def test_update_goods_by_external_id(self, uds_client):
        """Test updating goods by external ID."""
        external_id = "external-123"
        goods = GoodsDetailed(
            name="Updated Item",
            data=GoodsItemType(
                type=GoodsType.ITEM,
                price=150.0,
            ),
        )

        respx.put(
            f"https://api.uds.app/partner/v2/goods/external/{external_id}"
        ).mock(return_value=Response(200, json=GOODS_DETAIL_RESPONSE))

        result = await uds_client.goods.external.update(external_id, goods)

        assert isinstance(result, GoodsDetailed)

    async def test_delete_goods_by_external_id(self, uds_client):
        """Test deleting goods by external ID."""
        external_id = "external-123"

        respx.delete(
            f"https://api.uds.app/partner/v2/goods/external/{external_id}"
        ).mock(return_value=Response(204))

        await uds_client.goods.external.delete(external_id)

    async def test_goods_not_found(self, uds_client):
        """Test goods not found error."""
        from async_uds_api import UDSNotFoundError

        goods_id = 999999

        respx.get(f"https://api.uds.app/partner/v2/goods/{goods_id}").mock(
            return_value=Response(404, json={"message": "Not found"})
        )

        with pytest.raises(UDSNotFoundError):
            await uds_client.goods.get(goods_id)
