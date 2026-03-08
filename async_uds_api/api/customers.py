from typing import TYPE_CHECKING, Any, Dict, Optional

from ..models import CustomerDetail, CustomersPage, PurchaseCalcResponse

if TYPE_CHECKING:
    from ..client import UDSClient


class CustomersAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def list(
        self,
        *,
        max: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> CustomersPage:
        params: Dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        data = await self._client._get_json(
            "/customers", params=params or None
        )
        return CustomersPage.model_validate(data)

    async def find(
        self,
        *,
        code: Optional[str] = None,
        phone: Optional[str] = None,
        uid: Optional[str] = None,
        exchange_code: Optional[bool] = None,
        total: Optional[float] = None,
        skip_loyalty_total: Optional[float] = None,
        unredeemable_total: Optional[float] = None,
    ) -> PurchaseCalcResponse:
        params: Dict[str, Any] = {}
        if code is not None:
            params["code"] = code
        if phone is not None:
            params["phone"] = phone
        if uid is not None:
            params["uid"] = uid
        if exchange_code is not None:
            params["exchangeCode"] = exchange_code
        if total is not None:
            params["total"] = total
        if skip_loyalty_total is not None:
            params["skipLoyaltyTotal"] = skip_loyalty_total
        if unredeemable_total is not None:
            params["unredeemableTotal"] = unredeemable_total

        data = await self._client._get_json(
            "/customers/find", params=params or None
        )
        return PurchaseCalcResponse.model_validate(data)

    async def get(self, customer_id: int) -> CustomerDetail:
        data = await self._client._get_json(f"/customers/{customer_id}")
        return CustomerDetail.model_validate(data)
