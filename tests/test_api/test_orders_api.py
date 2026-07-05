import pytest
import respx
from httpx import Response

from async_uds_api import UDSNotFoundError
from async_uds_api.models import (
    GoodsOrderCode,
    GoodsOrderCompleteResult,
    GoodsOrderDetailed,
    GoodsOrderItem,
    GoodsOrderUpdateStatus,
)
from tests.fixtures.orders import (
    GOODS_ORDER_CODE_RESPONSE,
    GOODS_ORDER_COMPLETE_RESPONSE,
    GOODS_ORDER_RESPONSE,
)


class TestGoodsOrdersAPI:
    async def test_get_order_success(self, uds_client):
        respx.get("https://api.uds.app/partner/v2/goods-orders/42").mock(
            return_value=Response(200, json=GOODS_ORDER_RESPONSE)
        )

        result = await uds_client.goods_orders.get(42)

        assert isinstance(result, GoodsOrderDetailed)
        assert result.id == 42

    async def test_get_order_not_found(self, uds_client):
        respx.get("https://api.uds.app/partner/v2/goods-orders/999").mock(
            return_value=Response(404, json={"message": "Not found"})
        )

        with pytest.raises(UDSNotFoundError):
            await uds_client.goods_orders.get(999)

    async def test_update_order_success(self, uds_client):
        respx.put("https://api.uds.app/partner/v2/goods-orders/42").mock(
            return_value=Response(200, json=GOODS_ORDER_RESPONSE)
        )

        result = await uds_client.goods_orders.update(
            42, comment="Test comment"
        )

        assert isinstance(result, GoodsOrderDetailed)

    async def test_update_order_with_status(self, uds_client):
        respx.put("https://api.uds.app/partner/v2/goods-orders/42").mock(
            return_value=Response(200, json=GOODS_ORDER_RESPONSE)
        )

        result = await uds_client.goods_orders.update(
            42, order_status=GoodsOrderUpdateStatus.ACCEPTED
        )

        assert isinstance(result, GoodsOrderDetailed)

    async def test_update_order_with_items(self, uds_client):
        respx.put("https://api.uds.app/partner/v2/goods-orders/42").mock(
            return_value=Response(200, json=GOODS_ORDER_RESPONSE)
        )

        items = [
            GoodsOrderItem(
                id=1, name="Item A", type="ITEM", qty=1, price=100.0
            )
        ]
        result = await uds_client.goods_orders.update(42, items=items)

        assert isinstance(result, GoodsOrderDetailed)

    async def test_complete_order_success(self, uds_client):
        respx.post(
            "https://api.uds.app/partner/v2/goods-orders/42/complete"
        ).mock(return_value=Response(200, json=GOODS_ORDER_COMPLETE_RESPONSE))

        result = await uds_client.goods_orders.complete(42)

        assert isinstance(result, GoodsOrderCompleteResult)
        assert result.transaction is not None
        assert result.transaction.id == 777
        assert isinstance(result.order, GoodsOrderDetailed)
        assert result.order.id == 42

    async def test_generate_code_success(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/goods-orders/42/code").mock(
            return_value=Response(200, json=GOODS_ORDER_CODE_RESPONSE)
        )

        result = await uds_client.goods_orders.generate_code(42)

        assert isinstance(result, GoodsOrderCode)
        assert result.code == "123456"

    async def test_change_status_success(self, uds_client):
        respx.post(
            "https://api.uds.app/partner/v2/goods-orders/42/change-status"
        ).mock(return_value=Response(200, json=GOODS_ORDER_RESPONSE))

        result = await uds_client.goods_orders.change_status(
            42, status=GoodsOrderUpdateStatus.READY
        )

        assert isinstance(result, GoodsOrderDetailed)

    async def test_cancel_order_success(self, uds_client):
        respx.post(
            "https://api.uds.app/partner/v2/goods-orders/42/cancel"
        ).mock(return_value=Response(200, json=GOODS_ORDER_RESPONSE))

        result = await uds_client.goods_orders.cancel(42)

        assert isinstance(result, GoodsOrderDetailed)

    async def test_cancel_order_not_found(self, uds_client):
        respx.post(
            "https://api.uds.app/partner/v2/goods-orders/999/cancel"
        ).mock(return_value=Response(404, json={"message": "Not found"}))

        with pytest.raises(UDSNotFoundError):
            await uds_client.goods_orders.cancel(999)
