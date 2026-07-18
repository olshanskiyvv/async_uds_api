import logging

from async_uds_api.log import (
    SENSITIVE_PARAMS,
    StdlibLoggerAdapter,
    mask_params,
    mask_value,
)


class TestMaskValue:
    def test_keeps_last_four_characters(self):
        assert mask_value("+79991234567") == "***4567"

    def test_masks_short_value_completely(self):
        assert mask_value("1234") == "***"

    def test_masks_empty_value_completely(self):
        assert mask_value("") == "***"

    def test_converts_non_string_before_masking(self):
        assert mask_value(79991234567) == "***4567"

    def test_masks_uuid_tail(self):
        assert mask_value("9f8b1c2d-4e5f-6a7b-8c9d-0e1f2a3ba97e") == "***a97e"


class TestMaskParams:
    def test_masks_sensitive_keys(self):
        result = mask_params({"phone": "+79991234567", "uid": "abcd1234"})

        assert result == {"phone": "***4567", "uid": "***1234"}

    def test_keeps_other_keys_untouched(self):
        result = mask_params({"max": 50, "cursor": "abc"})

        assert result == {"max": 50, "cursor": "abc"}

    def test_masks_code(self):
        assert mask_params({"code": "998877"}) == {"code": "***8877"}

    def test_returns_none_for_none(self):
        assert mask_params(None) is None

    def test_does_not_mutate_input(self):
        source = {"phone": "+79991234567"}

        mask_params(source)

        assert source == {"phone": "+79991234567"}

    def test_sensitive_params_content(self):
        assert SENSITIVE_PARAMS == frozenset({"phone", "uid", "code"})


class TestStdlibLoggerAdapter:
    def test_renders_request_without_params(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info(
                "uds.request",
                method="GET",
                path="/customers",
                params=None,
                request_id="req-1",
                timestamp="2026-07-17T19:09:04+00:00",
            )

        assert caplog.messages == [
            "GET /customers [X-Origin-Request-Id=req-1] "
            "[X-Timestamp=2026-07-17T19:09:04+00:00]"
        ]

    def test_renders_request_with_params(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info(
                "uds.request",
                method="GET",
                path="/customers/find",
                params={"phone": "***4567"},
                request_id="req-1",
                timestamp="2026-07-17T19:09:04+00:00",
            )

        assert caplog.messages == [
            "GET /customers/find [phone=***4567] [X-Origin-Request-Id=req-1] "
            "[X-Timestamp=2026-07-17T19:09:04+00:00]"
        ]

    def test_renders_response(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info(
                "uds.response",
                method="GET",
                path="/customers",
                status=200,
                elapsed=0.3125,
            )

        assert caplog.messages == ["GET /customers -> 200 OK in 0.312s"]

    def test_renders_error_with_code(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.ERROR, logger="test.uds"):
            adapter.error(
                "uds.error",
                method="POST",
                path="/goods-orders/1/complete",
                status=404,
                elapsed=0.208,
                message="Order not found",
                error_code="notFound",
            )

        assert caplog.messages == [
            "POST /goods-orders/1/complete -> 404 Error in 0.208s: "
            "Order not found [errorCode=notFound]"
        ]

    def test_renders_error_without_code(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.ERROR, logger="test.uds"):
            adapter.error(
                "uds.error",
                method="POST",
                path="/operations",
                status=500,
                elapsed=1.5,
                message="Server error",
                error_code=None,
            )

        assert caplog.messages == [
            "POST /operations -> 500 Error in 1.500s: Server error"
        ]

    def test_renders_retry(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.WARNING, logger="test.uds"):
            adapter.warning(
                "uds.retry", method="POST", path="/operations", attempt=2
            )

        assert caplog.messages == ["Retry attempt 2 for POST /operations"]

    def test_unknown_event_falls_back_to_key_value(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug("uds.custom", alpha=1, beta="two")

        assert caplog.messages == ["uds.custom alpha=1 beta=two"]

    def test_missing_template_field_falls_back(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info("uds.response", method="GET")

        assert caplog.messages == ["uds.response method=GET"]

    def test_passes_raw_fields_to_extra(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info(
                "uds.request",
                method="GET",
                path="/customers/find",
                params={"phone": "***4567"},
                request_id="req-1",
                timestamp="ts",
            )

        assert caplog.records[0].uds["params"] == {"phone": "***4567"}
        assert caplog.records[0].uds["method"] == "GET"

    def test_respects_logger_level(self, caplog):
        logger = logging.getLogger("test.uds.level")
        adapter = StdlibLoggerAdapter(logger)

        with caplog.at_level(logging.WARNING, logger="test.uds.level"):
            adapter.debug("uds.custom", alpha=1)

        assert caplog.messages == []
