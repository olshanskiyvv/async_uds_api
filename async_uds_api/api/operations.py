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
    ) -> OperationsPage:
        params: dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        data = await self._client._get_json(
            "/operations", params=params or None
        )
        return OperationsPage.model_validate(data)

    async def iter_all(
        self, *, page_size: int = 50
    ) -> AsyncIterator[Operation]:
        cursor: str | None = None
        while True:
            page = await self.list(max=page_size, cursor=cursor)
            for row in page.rows:
                yield row
            if not page.rows or page.cursor is None:
                break
            cursor = page.cursor

    async def create(self, operation: CreateOperation) -> Operation:
        body = operation.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json("/operations", body=body)
        return Operation.model_validate(data)

    async def get(self, operation_id: int) -> Operation:
        data = await self._client._get_json(f"/operations/{operation_id}")
        return Operation.model_validate(data)

    async def refund(
        self,
        operation_id: int,
        refund: RefundOperationRequest | None = None,
    ) -> Operation:
        body = (
            refund.model_dump(by_alias=True, exclude_none=True)
            if refund
            else None
        )
        data = await self._client._post_json(
            f"/operations/{operation_id}/refund",
            body=body,
        )
        return Operation.model_validate(data)

    async def calc(
        self,
        calc_request: PurchaseCalcRequest,
    ) -> PurchaseCalcResponse:
        body = calc_request.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json("/operations/calc", body=body)
        return PurchaseCalcResponse.model_validate(data)

    async def reward(
        self,
        reward_request: RewardRequest,
    ) -> None:
        body = reward_request.model_dump(by_alias=True, exclude_none=True)
        await self._client._post_json("/operations/reward", body=body)

    async def create_voucher(self, voucher: CreateVoucher) -> VoucherInfo:
        body = voucher.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json("/operations/voucher", body=body)
        return VoucherInfo.model_validate(data)
