import builtins
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from async_uds_api.models import (
    Customer,
    CustomerDetail,
    CustomersPage,
    FindCustomerResponse,
    TagsPage,
)

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class CustomersAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def list(
        self,
        *,
        max: int | None = None,
        offset: int | None = None,
        cursor: str | None = None,
        request_id: str | None = None,
    ) -> CustomersPage:
        """Return a page of customers, filtered by cursor or offset."""
        params: dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        data = await self._client._get_json(
            "/customers", params=params or None, request_id=request_id
        )
        return CustomersPage.model_validate(data)

    async def iter_all(
        self, *, page_size: int = 50, request_id: str | None = None
    ) -> AsyncIterator[Customer]:
        """Yield every customer, fetching pages transparently via cursor.

        The explicit request_id parameter, if given, is sent for every
        page. A value bound via use_origin_request_id is not: an async
        generator does not capture the context of the block where it
        was created, so pages pulled after that block exits get a
        freshly generated uuid4.
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

    async def find(
        self,
        *,
        code: str | None = None,
        phone: str | None = None,
        uid: str | None = None,
        exchange_code: bool | None = None,
        total: float | None = None,
        skip_loyalty_total: float | None = None,
        unredeemable_total: float | None = None,
        request_id: str | None = None,
    ) -> FindCustomerResponse:
        """Find a customer by code, phone, or uid."""
        params: dict[str, Any] = {}
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
            "/customers/find", params=params or None, request_id=request_id
        )
        return FindCustomerResponse.model_validate(data)

    async def get(
        self, customer_id: int, *, request_id: str | None = None
    ) -> CustomerDetail:
        """Return customer details including participant stats and tags."""
        data = await self._client._get_json(
            f"/customers/{customer_id}", request_id=request_id
        )
        return CustomerDetail.model_validate(data)

    async def get_tags(
        self, customer_id: int, *, request_id: str | None = None
    ) -> TagsPage:
        """Return tags currently assigned to a customer."""
        data = await self._client._get_json(
            f"/customers/{customer_id}/tags", request_id=request_id
        )
        return TagsPage.model_validate(data)

    async def set_tags(
        self,
        customer_id: int,
        tag_ids: builtins.list[int],
        *,
        request_id: str | None = None,
    ) -> TagsPage:
        """Replace all tags for a customer with the given list of tag IDs."""
        body = {"ids": tag_ids}
        data = await self._client._post_json(
            f"/customers/{customer_id}/tags",
            body=body,
            request_id=request_id,
        )
        return TagsPage.model_validate(data)
