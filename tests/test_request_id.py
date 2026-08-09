import asyncio

import pytest

from async_uds_api import (
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
