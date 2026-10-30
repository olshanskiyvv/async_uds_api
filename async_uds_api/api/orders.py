from typing import TYPE_CHECKING, Any

from async_uds_api.models import (
    DeliveryCase,
    GoodsOrderCode,
    GoodsOrderCompleteResult,
    GoodsOrderDetailed,
    GoodsOrderItemNew,
    GoodsOrderItemUpdate,
    GoodsOrderUpdateStatus,
)

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class GoodsOrdersAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def get(
        self, order_id: int, *, request_id: str | None = None
    ) -> GoodsOrderDetailed:
        """Return a goods order by its ID."""
        data = await self._client._get_json(
            f"/goods-orders/{order_id}", request_id=request_id
        )
        return GoodsOrderDetailed.model_validate(data)

    async def update(
        self,
        order_id: int,
        *,
        delivery_case: DeliveryCase | None = None,
        items: list[GoodsOrderItemUpdate | GoodsOrderItemNew] | None = None,
        request_id: str | None = None,
    ) -> GoodsOrderDetailed:
        """Update order delivery case or line items."""
        body: dict[str, Any] = {}
        if delivery_case is not None:
            body["deliveryCase"] = delivery_case.model_dump(
                by_alias=True, exclude_none=True
            )
        if items is not None:
            body["items"] = [
                item.model_dump(by_alias=True, exclude_none=True)
                for item in items
            ]

        data = await self._client._put_json(
            f"/goods-orders/{order_id}",
            body=body or None,
            request_id=request_id,
        )
        return GoodsOrderDetailed.model_validate(data)

    async def complete(
        self, order_id: int, *, request_id: str | None = None
    ) -> GoodsOrderCompleteResult:
        """Mark an order as completed (goods handed to the customer)."""
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/complete",
            body=None,
            request_id=request_id,
        )
        return GoodsOrderCompleteResult.model_validate(data)

    async def generate_code(
        self, order_id: int, *, request_id: str | None = None
    ) -> GoodsOrderCode:
        """Generate a one-time verification code for order pick-up."""
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/code",
            body=None,
            request_id=request_id,
        )
        return GoodsOrderCode.model_validate(data)

    async def change_status(
        self,
        order_id: int,
        status: GoodsOrderUpdateStatus,
        *,
        request_id: str | None = None,
    ) -> GoodsOrderDetailed:
        """Transition an order to the given status."""
        body = {"orderStatus": status.value}
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/change-status",
            body=body,
            request_id=request_id,
        )
        return GoodsOrderDetailed.model_validate(data)

    async def cancel(
        self, order_id: int, *, request_id: str | None = None
    ) -> GoodsOrderDetailed:
        """Cancel an order."""
        data = await self._client._post_json(
            f"/goods-orders/{order_id}/cancel",
            body=None,
            request_id=request_id,
        )
        return GoodsOrderDetailed.model_validate(data)
