import asyncio
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
            with use_origin_request_id("sibling"):
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
