import pytest
import respx
from httpx import Response

from async_uds_api.models import (
    GoodsDetailed,
    GoodsItemType,
    GoodsPage,
)
from tests.fixtures.goods import GOODS_DETAIL_RESPONSE, GOODS_LIST_RESPONSE


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
                type="ITEM",
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
                type="ITEM",
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
                type="ITEM",
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

    async def test_iter_all_goods_single_page(self, uds_client):
        respx.get(
            "https://api.uds.app/partner/v2/goods",
            params={"max": "50", "offset": "0"},
        ).mock(return_value=Response(200, json=GOODS_LIST_RESPONSE))

        result = [g async for g in uds_client.goods.iter_all()]

        assert len(result) == 1

    async def test_iter_all_goods_multiple_pages(self, uds_client):
        row = GOODS_LIST_RESPONSE["rows"][0]
        responses = [
            Response(200, json={"rows": [row], "total": 3}),
            Response(200, json={"rows": [row], "total": 3}),
            Response(200, json={"rows": [], "total": 3}),
        ]

        def handler(request):  # type: ignore[no-untyped-def]
            return responses.pop(0)

        respx.get("https://api.uds.app/partner/v2/goods").mock(
            side_effect=handler
        )

        result = [g async for g in uds_client.goods.iter_all(page_size=1)]

        assert len(result) == 2

    async def test_iter_all_goods_with_node_id(self, uds_client):
        respx.get(
            "https://api.uds.app/partner/v2/goods",
            params={"max": "50", "offset": "0", "nodeId": "5"},
        ).mock(return_value=Response(200, json=GOODS_LIST_RESPONSE))

        result = [g async for g in uds_client.goods.iter_all(node_id=5)]

        assert len(result) == 1

    async def test_iter_all_goods_empty(self, uds_client):
        respx.get(
            "https://api.uds.app/partner/v2/goods",
            params={"max": "50", "offset": "0"},
        ).mock(return_value=Response(200, json={"rows": [], "total": 0}))

        result = [g async for g in uds_client.goods.iter_all()]

        assert result == []

    async def test_goods_not_found(self, uds_client):
        """Test goods not found error."""
        from async_uds_api import UDSNotFoundError

        goods_id = 999999

        respx.get(f"https://api.uds.app/partner/v2/goods/{goods_id}").mock(
            return_value=Response(404, json={"message": "Not found"})
        )

        with pytest.raises(UDSNotFoundError):
            await uds_client.goods.get(goods_id)
