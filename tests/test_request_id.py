import asyncio
import time
import uuid

import httpx
import pytest
import respx

from async_uds_api import (
    UDSClient,
    get_origin_request_id,
    reset_origin_request_id,
    set_origin_request_id,
    use_origin_request_id,
)
from tests.fixtures.settings import COMPANY_SETTINGS_RESPONSE


class TestContextVarAccessors:
    def test_default_is_none(self):
        assert get_origin_request_id() is None

    def test_set_then_get(self):
        token = set_origin_request_id("trace-1")
        try:
            assert get_origin_request_id() == "trace-1"
        finally:
            reset_origin_request_id(token)

    def test_reset_restores_previous_value(self):
        outer = set_origin_request_id("outer")
        inner = set_origin_request_id("inner")
        assert get_origin_request_id() == "inner"
        reset_origin_request_id(inner)
        assert get_origin_request_id() == "outer"
        reset_origin_request_id(outer)
        assert get_origin_request_id() is None

    def test_accepts_arbitrary_non_uuid_string(self):
        token = set_origin_request_id("не-uuid: 42 / abc")
        try:
            assert get_origin_request_id() == "не-uuid: 42 / abc"
        finally:
            reset_origin_request_id(token)

    def test_set_none_clears_value(self):
        outer = set_origin_request_id("trace-1")
        inner = set_origin_request_id(None)
        try:
            assert get_origin_request_id() is None
        finally:
            reset_origin_request_id(inner)
            reset_origin_request_id(outer)


class TestUseOriginRequestId:
    def test_sets_value_inside_block(self):
        with use_origin_request_id("trace-1"):
            assert get_origin_request_id() == "trace-1"
        assert get_origin_request_id() is None

    def test_yields_the_value(self):
        with use_origin_request_id("trace-1") as value:
            assert value == "trace-1"

    def test_restores_previous_value_on_exit(self):
        with use_origin_request_id("outer"):
            with use_origin_request_id("inner"):
                assert get_origin_request_id() == "inner"
            assert get_origin_request_id() == "outer"
        assert get_origin_request_id() is None

    def test_restores_previous_value_on_exception(self):
        with pytest.raises(RuntimeError):
            with use_origin_request_id("trace-1"):
                raise RuntimeError("boom")
        assert get_origin_request_id() is None


class TestTaskIsolation:
    async def test_value_does_not_leak_between_tasks(self):
        seen: list[str | None] = []

        async def child() -> None:
            seen.append(get_origin_request_id())

        with use_origin_request_id("parent"):
            await asyncio.gather(child())
            inherited = seen[-1]

        async def sibling() -> None:
            set_origin_request_id("sibling")
            await asyncio.sleep(0)

        await asyncio.gather(sibling())

        assert inherited == "parent"
        assert get_origin_request_id() is None


class TestHeaderResolution:
    def _client(self):
        return UDSClient(company_id="123456", api_key="test-api-key")

    def test_generates_uuid_when_nothing_is_set(self):
        headers = self._client()._build_headers()

        uuid.UUID(headers["X-Origin-Request-Id"])

    def test_uses_contextvar_value(self):
        client = self._client()

        with use_origin_request_id("trace-ctx"):
            headers = client._build_headers()

        assert headers["X-Origin-Request-Id"] == "trace-ctx"

    def test_explicit_value_wins_over_contextvar(self):
        client = self._client()

        with use_origin_request_id("trace-ctx"):
            headers = client._build_headers("trace-explicit")

        assert headers["X-Origin-Request-Id"] == "trace-explicit"

    def test_empty_explicit_value_falls_back_to_contextvar(self):
        client = self._client()

        with use_origin_request_id("trace-ctx"):
            headers = client._build_headers("")

        assert headers["X-Origin-Request-Id"] == "trace-ctx"

    def test_empty_contextvar_value_falls_back_to_uuid(self):
        client = self._client()

        with use_origin_request_id(""):
            headers = client._build_headers()

        uuid.UUID(headers["X-Origin-Request-Id"])

    def test_arbitrary_string_is_sent_verbatim(self):
        client = self._client()

        headers = client._build_headers("order-42/attempt-1")

        assert headers["X-Origin-Request-Id"] == "order-42/attempt-1"


class TestRequestIdReachesTheWire:
    async def test_contextvar_value_is_sent_in_header(self, uds_client):
        route = respx.get("https://api.uds.app/partner/v2/customers").mock(
            return_value=httpx.Response(200, json={"rows": []})
        )

        with use_origin_request_id("trace-ctx"):
            await uds_client._get_json("/customers")

        sent = route.calls[0].request
        assert sent.headers["X-Origin-Request-Id"] == "trace-ctx"

    async def test_explicit_value_is_sent_in_header(self, uds_client):
        route = respx.get("https://api.uds.app/partner/v2/customers").mock(
            return_value=httpx.Response(200, json={"rows": []})
        )

        await uds_client._get_json("/customers", request_id="trace-arg")

        sent = route.calls[0].request
        assert sent.headers["X-Origin-Request-Id"] == "trace-arg"

    async def test_same_id_on_every_call_in_the_block(self, uds_client):
        route = respx.get("https://api.uds.app/partner/v2/customers").mock(
            return_value=httpx.Response(200, json={"rows": []})
        )

        with use_origin_request_id("trace-chain"):
            await uds_client._get_json("/customers")
            await uds_client._get_json("/customers")

        ids = [
            call.request.headers["X-Origin-Request-Id"] for call in route.calls
        ]
        assert ids == ["trace-chain", "trace-chain"]

    async def test_same_id_on_every_retry_attempt(self, mock_httpx):
        route = respx.get("https://api.uds.app/partner/v2/customers")
        route.side_effect = [
            httpx.Response(500, json={"message": "server error"}),
            httpx.Response(200, json={"rows": []}),
        ]

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=2
        ) as client:
            with use_origin_request_id("trace-retry"):
                await client._get_json("/customers")

        ids = [
            call.request.headers["X-Origin-Request-Id"] for call in route.calls
        ]
        assert ids == ["trace-retry", "trace-retry"]

    async def test_generated_ids_differ_between_retry_attempts(
        self, mock_httpx
    ):
        route = respx.get("https://api.uds.app/partner/v2/customers")
        route.side_effect = [
            httpx.Response(500, json={"message": "server error"}),
            httpx.Response(200, json={"rows": []}),
        ]

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=2
        ) as client:
            await client._get_json("/customers")

        ids = {
            call.request.headers["X-Origin-Request-Id"] for call in route.calls
        }
        assert len(ids) == 2


class TestExplicitParamInApiMethods:
    async def test_customers_find(self, uds_client):
        route = respx.get(
            "https://api.uds.app/partner/v2/customers/find"
        ).mock(return_value=httpx.Response(200, json={"user": {}}))

        await uds_client.customers.find(
            code="1234", request_id="trace-customers"
        )

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-customers"
        )

    async def test_customers_iter_all_uses_one_id_for_all_pages(
        self, uds_client
    ):
        route = respx.get("https://api.uds.app/partner/v2/customers")
        route.side_effect = [
            httpx.Response(
                200, json={"rows": [{"uid": "u-1"}], "cursor": "next"}
            ),
            httpx.Response(200, json={"rows": [], "cursor": None}),
        ]

        rows = [
            row
            async for row in uds_client.customers.iter_all(
                page_size=1, request_id="trace-pages"
            )
        ]

        ids = [
            call.request.headers["X-Origin-Request-Id"] for call in route.calls
        ]
        assert len(rows) == 1
        assert ids == ["trace-pages", "trace-pages"]

    async def test_operations_get(self, uds_client):
        route = respx.get("https://api.uds.app/partner/v2/operations/7").mock(
            return_value=httpx.Response(
                200, json={"id": 7, "action": "PURCHASE"}
            )
        )

        await uds_client.operations.get(7, request_id="trace-operations")

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-operations"
        )

    async def test_tags_list(self, uds_client):
        route = respx.get("https://api.uds.app/partner/v2/tags").mock(
            return_value=httpx.Response(200, json={"rows": []})
        )

        await uds_client.tags.list(request_id="trace-tags")

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-tags"
        )

    async def test_settings_get(self, uds_client):
        route = respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=httpx.Response(
                200,
                json={
                    "id": 123456,
                    "name": "Test Company",
                    "promoCode": "TEST",
                    "baseDiscountPolicy": "CHARGE_SCORES",
                    "purchaseByPhone": True,
                    "usePointsByPhone": True,
                    "writeInvoice": False,
                    "slug": "test-company",
                },
            )
        )

        await uds_client.settings.get(request_id="trace-settings")

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-settings"
        )


class TestExplicitParamInRemainingModules:
    async def test_goods_delete(self, uds_client):
        route = respx.delete("https://api.uds.app/partner/v2/goods/5").mock(
            return_value=httpx.Response(200, json={})
        )

        await uds_client.goods.delete(5, request_id="trace-goods")

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-goods"
        )

    async def test_goods_external_delete(self, uds_client):
        route = respx.delete(
            "https://api.uds.app/partner/v2/goods/external/sku-1"
        ).mock(return_value=httpx.Response(200, json={}))

        await uds_client.goods.external.delete(
            "sku-1", request_id="trace-external"
        )

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-external"
        )

    async def test_orders_cancel(self, uds_client):
        route = respx.post(
            "https://api.uds.app/partner/v2/goods-orders/3/cancel"
        ).mock(return_value=httpx.Response(200, json={"purchase": {}}))

        await uds_client.goods_orders.cancel(3, request_id="trace-orders")

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-orders"
        )

    async def test_images_get_upload_url(self, uds_client):
        route = respx.post(
            "https://api.uds.app/partner/v2/image-upload-url"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "imageId": "img-1",
                    "method": "PUT",
                    "url": "https://storage.example.com/img-1",
                },
            )
        )

        await uds_client.images.get_upload_url(
            "image/jpeg", request_id="trace-images"
        )

        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-images"
        )


class TestImagesUploadOmitsHeaderOnStorage:
    async def test_presigned_upload_carries_no_origin_header(self, uds_client):
        upload_url_route = respx.post(
            "https://api.uds.app/partner/v2/image-upload-url"
        ).mock(
            return_value=httpx.Response(
                200,
                json={
                    "imageId": "img-1",
                    "method": "PUT",
                    "url": "https://storage.example.com/img-1",
                },
            )
        )
        storage_route = respx.put("https://storage.example.com/img-1").mock(
            return_value=httpx.Response(200)
        )

        await uds_client.images.upload(
            b"image data", "image/jpeg", request_id="trace-upload"
        )

        assert (
            upload_url_route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-upload"
        )
        assert (
            "X-Origin-Request-Id" not in storage_route.calls[0].request.headers
        )


class TestSettingsCacheIgnoresRequestId:
    async def test_cache_hit_skips_request_and_ignores_request_id(
        self, uds_client
    ):
        route = respx.get("https://api.uds.app/partner/v2/settings").mock(
            return_value=httpx.Response(200, json=COMPANY_SETTINGS_RESPONSE)
        )

        first = await uds_client.settings.get(request_id="trace-first")
        second = await uds_client.settings.get(request_id="trace-second")

        assert route.call_count == 1
        assert first is second
        assert (
            route.calls[0].request.headers["X-Origin-Request-Id"]
            == "trace-first"
        )


class TestLocalProtocolErrorIsNotRetried:
    async def test_header_injection_value_raises_without_retry(self):
        connections = 0

        async def handle(
            reader: asyncio.StreamReader,
            writer: asyncio.StreamWriter,
        ) -> None:
            nonlocal connections
            connections += 1
            await reader.read(65536)
            writer.close()

        server = await asyncio.start_server(handle, "127.0.0.1", 0)
        port = server.sockets[0].getsockname()[1]

        async with server:
            async with UDSClient(
                company_id="123456",
                api_key="test-api-key",
                base_url=f"http://127.0.0.1:{port}",
                retries=3,
            ) as client:
                start = time.monotonic()
                with pytest.raises(httpx.LocalProtocolError):
                    await client._get_json(
                        "/customers", request_id="bad\r\nvalue"
                    )
                elapsed = time.monotonic() - start

        assert connections == 1
        assert elapsed < 1.0
