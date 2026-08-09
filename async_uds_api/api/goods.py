from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any

from async_uds_api.models import GoodsDetailed, GoodsInfoType, GoodsPage

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class GoodsExternalAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def get(
        self, external_id: str, *, request_id: str | None = None
    ) -> GoodsDetailed:
        """Return a goods item by its external (partner-side) ID."""
        data = await self._client._get_json(
            f"/goods/external/{external_id}", request_id=request_id
        )
        return GoodsDetailed.model_validate(data)

    async def update(
        self,
        external_id: str,
        goods: GoodsDetailed,
        *,
        request_id: str | None = None,
    ) -> GoodsDetailed:
        """Update a goods item identified by its external ID."""
        body = goods.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._put_json(
            f"/goods/external/{external_id}",
            body=body,
            request_id=request_id,
        )
        return GoodsDetailed.model_validate(data)

    async def delete(
        self, external_id: str, *, request_id: str | None = None
    ) -> None:
        """Delete a goods item by its external ID."""
        await self._client._delete(
            f"/goods/external/{external_id}", request_id=request_id
        )


class GoodsAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client
        self.external = GoodsExternalAPI(client)

    async def list(
        self,
        *,
        max: int | None = None,
        offset: int | None = None,
        node_id: int | None = None,
        request_id: str | None = None,
    ) -> GoodsPage:
        """Return a page of goods, optionally scoped to a catalogue node."""
        params: dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if node_id is not None:
            params["nodeId"] = node_id

        data = await self._client._get_json(
            "/goods", params=params or None, request_id=request_id
        )
        return GoodsPage.model_validate(data)

    async def iter_all(
        self,
        *,
        page_size: int = 50,
        node_id: int | None = None,
        request_id: str | None = None,
    ) -> AsyncIterator[GoodsInfoType]:
        """Yield every goods item, fetching pages transparently via offset.

        The same request_id is sent for every page.
        """
        offset = 0
        while True:
            page = await self.list(
                max=page_size,
                offset=offset,
                node_id=node_id,
                request_id=request_id,
            )
            for row in page.rows:
                yield row
            if len(page.rows) < page_size:
                break
            offset += len(page.rows)

    async def create(
        self, goods: GoodsDetailed, *, request_id: str | None = None
    ) -> GoodsDetailed:
        """Create a new goods item in the catalogue."""
        body = goods.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json(
            "/goods", body=body, request_id=request_id
        )
        return GoodsDetailed.model_validate(data)

    async def get(
        self, goods_id: int, *, request_id: str | None = None
    ) -> GoodsDetailed:
        """Return a goods item by its UDS ID."""
        data = await self._client._get_json(
            f"/goods/{goods_id}", request_id=request_id
        )
        return GoodsDetailed.model_validate(data)

    async def update(
        self,
        goods_id: int,
        goods: GoodsDetailed,
        *,
        request_id: str | None = None,
    ) -> GoodsDetailed:
        """Update a goods item by its UDS ID."""
        body = goods.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._put_json(
            f"/goods/{goods_id}", body=body, request_id=request_id
        )
        return GoodsDetailed.model_validate(data)

    async def delete(
        self, goods_id: int, *, request_id: str | None = None
    ) -> None:
        """Delete a goods item by its UDS ID."""
        await self._client._delete(f"/goods/{goods_id}", request_id=request_id)
