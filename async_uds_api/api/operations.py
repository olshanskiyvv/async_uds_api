from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from async_uds_api.models import (
    CreateOperation,
    CreateVoucher,
    Operation,
    OperationsPage,
    PurchaseCalcRequest,
    PurchaseCalcResponse,
    RefundOperationRequest,
    RewardRequest,
    VoucherInfo,
)

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class OperationsAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def list(
        self,
        *,
        max: int | None = None,
        offset: int | None = None,
        cursor: str | None = None,
        request_id: str | None = None,
    ) -> OperationsPage:
        """Return a page of operations, filtered by cursor or offset."""
        params: dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        data = await self._client._get_json(
            "/operations", params=params or None, request_id=request_id
        )
        return OperationsPage.model_validate(data)

    async def iter_all(
        self, *, page_size: int = 50, request_id: str | None = None
    ) -> AsyncIterator[Operation]:
        """Yield every operation, fetching pages transparently via cursor.

        The same request_id is sent for every page.
        """
        cursor: str | None = None
        while True:
            page = await self.list(
                max=page_size, cursor=cursor, request_id=request_id
            )
            for row in page.rows:
                yield row
            if not page.rows or page.cursor is None:
                break
            cursor = page.cursor

    async def create(
        self,
        operation: CreateOperation,
        *,
        request_id: str | None = None,
    ) -> Operation:
        """Create a new purchase or reward operation."""
        body = operation.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json(
            "/operations", body=body, request_id=request_id
        )
        return Operation.model_validate(data)

    async def get(
        self, operation_id: int, *, request_id: str | None = None
    ) -> Operation:
        """Return an operation by its ID."""
        data = await self._client._get_json(
            f"/operations/{operation_id}", request_id=request_id
        )
        return Operation.model_validate(data)

    async def refund(
        self,
        operation_id: int,
        refund: RefundOperationRequest | None = None,
        *,
        request_id: str | None = None,
    ) -> Operation:
        """Refund an operation; pass RefundOperationRequest for partial."""
        body = (
            refund.model_dump(by_alias=True, exclude_none=True)
            if refund
            else None
        )
        data = await self._client._post_json(
            f"/operations/{operation_id}/refund",
            body=body,
            request_id=request_id,
        )
        return Operation.model_validate(data)

    async def calc(
        self,
        calc_request: PurchaseCalcRequest,
        *,
        request_id: str | None = None,
    ) -> PurchaseCalcResponse:
        """Calculate applicable discounts and points for a purchase."""
        body = calc_request.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json(
            "/operations/calc", body=body, request_id=request_id
        )
        return PurchaseCalcResponse.model_validate(data)

    async def reward(
        self,
        reward_request: RewardRequest,
        *,
        request_id: str | None = None,
    ) -> None:
        """Issue a non-purchase reward (e.g. referral bonus) to a customer."""
        body = reward_request.model_dump(by_alias=True, exclude_none=True)
        await self._client._post_json(
            "/operations/reward", body=body, request_id=request_id
        )

    async def create_voucher(
        self, voucher: CreateVoucher, *, request_id: str | None = None
    ) -> VoucherInfo:
        """Create a new voucher and return its details."""
        body = voucher.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json(
            "/operations/voucher", body=body, request_id=request_id
        )
        return VoucherInfo.model_validate(data)
