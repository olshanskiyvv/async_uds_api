from typing import TYPE_CHECKING, Any

from async_uds_api.models import (
    GoodsOrderCode,
    GoodsOrderDetailed,
    GoodsOrderItem,
    GoodsOrderUpdateStatus,
)

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class GoodsOrdersAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def get(self, order_id: int) -> GoodsOrderDetailed:
        data = await self._client._get_json(f"/goods-orders/{order_id}")
        return GoodsOrderDetailed.model_validate(data)

    async def update(
        self,
        order_id: int,
        *,
        order_status: GoodsOrderUpdateStatus | None = None,
        items: list[GoodsOrderItem] | None = None,
        comment: str | None = None,
    ) -> GoodsOrderDetailed:
        body: dict[str, Any] = {}
        if order_status is not None:
            body["orderStatus"] = order_status.value
        if items is not None:
            body["items"] = [
                item.model_dump(by_alias=True, exclude_none=True)
                for item in items
            ]
        if comment is not None:
            body["comment"] = comment

        data = await self._client._put_json(
            f"/goods-orders/{order_id}",
            body=body or None,
        )
        return GoodsOrderDetailed.model_validate(data)

    async def complete(self, order_id: int) -> GoodsOrderDetailed:
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/complete",
            body=None,
        )
        return GoodsOrderDetailed.model_validate(data)

    async def generate_code(self, order_id: int) -> GoodsOrderCode:
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/code",
            body=None,
        )
        return GoodsOrderCode.model_validate(data)

    async def change_status(
        self,
        order_id: int,
        status: GoodsOrderUpdateStatus,
    ) -> GoodsOrderDetailed:
        body = {"orderStatus": status.value}
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/change-status",
            body=body,
        )
        return GoodsOrderDetailed.model_validate(data)

    async def cancel(self, order_id: int) -> GoodsOrderDetailed:
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/cancel",
            body=None,
        )
        return GoodsOrderDetailed.model_validate(data)
