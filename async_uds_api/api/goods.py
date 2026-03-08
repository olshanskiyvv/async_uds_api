from typing import TYPE_CHECKING, Any

from async_uds_api.models import GoodsDetailed, GoodsPage

if TYPE_CHECKING:
    from async_uds_api.client import UDSClient


class GoodsExternalAPI:
    def __init__(self, client: "UDSClient") -> None:
        self._client = client

    async def get(self, external_id: str) -> GoodsDetailed:
        data = await self._client._get_json(f"/goods/external/{external_id}")
        return GoodsDetailed.model_validate(data)

    async def update(
        self,
        external_id: str,
        goods: GoodsDetailed,
    ) -> GoodsDetailed:
        body = goods.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._put_json(
            f"/goods/external/{external_id}", body=body
        )
        return GoodsDetailed.model_validate(data)

    async def delete(self, external_id: str) -> None:
        await self._client._delete(f"/goods/external/{external_id}")


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
    ) -> GoodsPage:
        params: dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if node_id is not None:
            params["nodeId"] = node_id

        data = await self._client._get_json("/goods", params=params or None)
        return GoodsPage.model_validate(data)

    async def create(self, goods: GoodsDetailed) -> GoodsDetailed:
        body = goods.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json("/goods", body=body)
        return GoodsDetailed.model_validate(data)

    async def get(self, goods_id: int) -> GoodsDetailed:
        data = await self._client._get_json(f"/goods/{goods_id}")
        return GoodsDetailed.model_validate(data)

    async def update(
        self, goods_id: int, goods: GoodsDetailed
    ) -> GoodsDetailed:
        body = goods.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._put_json(f"/goods/{goods_id}", body=body)
        return GoodsDetailed.model_validate(data)

    async def delete(self, goods_id: int) -> None:
        await self._client._delete(f"/goods/{goods_id}")
