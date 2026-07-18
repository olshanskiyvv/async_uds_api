import logging

import pytest

from async_uds_api.log import (
    SENSITIVE_PARAMS,
    StdlibLoggerAdapter,
    mask_params,
    mask_url,
    mask_value,
)


class TestMaskValue:
    def test_keeps_last_four_characters(self):
        assert mask_value("+79991234567") == "***4567"

    def test_masks_short_value_completely(self):
        assert mask_value("1234") == "***"

    def test_masks_empty_value_completely(self):
        assert mask_value("") == "***"

    def test_masks_none_completely(self):
        assert mask_value(None) == "***"

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

    def test_masks_none_sensitive_value(self):
        assert mask_params({"uid": None}) == {"uid": "***"}


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
                error_code="notFound",
            )

        assert caplog.messages == [
            "POST /goods-orders/1/complete -> 404 Error in 0.208s "
            "[errorCode=notFound]"
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
                error_code=None,
            )

        assert caplog.messages == ["POST /operations -> 500 Error in 1.500s"]

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

    def test_non_mapping_params_falls_back(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info(
                "uds.request",
                method="GET",
                path="/customers",
                params="not-a-mapping",
                request_id="req-1",
                timestamp="2026-07-17T19:09:04+00:00",
            )

        assert caplog.messages == [
            "uds.request method=GET path=/customers params=not-a-mapping "
            "request_id=req-1 timestamp=2026-07-17T19:09:04+00:00"
        ]

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

    def test_logging_never_raises_on_broken_field(self, caplog):
        class Explodes:
            def __str__(self):
                raise RuntimeError("boom")

        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds.broken"))

        with caplog.at_level(logging.INFO, logger="test.uds.broken"):
            adapter.info(
                "uds.request", method="GET", path="/x", bad=Explodes()
            )

        assert len(caplog.records) == 1
        message = caplog.records[0].getMessage()
        assert message.startswith("uds.request")
        assert "method=GET" in message
        assert "path=/x" in message
        assert caplog.records[0].uds["method"] == "GET"


class TestImageTemplates:
    def test_renders_upload_url_request(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug(
                "uds.image.upload_url_request", content_type="image/png"
            )

        assert caplog.messages == [
            "Requesting upload URL for content_type=image/png"
        ]

    def test_renders_upload_url_received(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info("uds.image.upload_url_received", image_id="img-1")

        assert caplog.messages == ["Got upload URL: image_id=img-1"]

    def test_renders_upload_start_bytes(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug(
                "uds.image.upload_start_bytes",
                size=1024,
                content_type="image/jpeg",
            )

        assert caplog.messages == [
            "Uploading 1024 bytes with content_type=image/jpeg"
        ]

    def test_renders_upload_start_source(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug(
                "uds.image.upload_start_source",
                source="/tmp/x.png",
                content_type="image/png",
            )

        assert caplog.messages == [
            "Uploading from /tmp/x.png with content_type=image/png"
        ]

    def test_renders_read(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug("uds.image.read", size=2048)

        assert caplog.messages == ["Read 2048 bytes"]

    def test_renders_uploaded(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.INFO, logger="test.uds"):
            adapter.info("uds.image.uploaded", image_id="img-2")

        assert caplog.messages == [
            "Image uploaded successfully: image_id=img-2"
        ]

    def test_renders_file_read_start(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug("uds.image.file_read_start", path="/tmp/x.png")

        assert caplog.messages == ["Reading image from file: /tmp/x.png"]

    def test_renders_file_read_done(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug(
                "uds.image.file_read_done", size=1024, path="/tmp/x.png"
            )

        assert caplog.messages == ["Read 1024 bytes from /tmp/x.png"]

    def test_renders_file_not_found(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.ERROR, logger="test.uds"):
            adapter.error("uds.image.file_not_found", path="/tmp/x.png")

        assert caplog.messages == ["File not found: /tmp/x.png"]

    def test_renders_file_read_failed(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.ERROR, logger="test.uds"):
            adapter.error(
                "uds.image.file_read_failed",
                path="/tmp/x.png",
                error="boom",
            )

        assert caplog.messages == ["Failed to read file /tmp/x.png: boom"]

    def test_renders_download_start(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug("uds.image.download_start", url="https://x/y.png")

        assert caplog.messages == [
            "Downloading image from URL: https://x/y.png"
        ]

    def test_renders_download_done(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug(
                "uds.image.download_done", size=512, url="https://x/y.png"
            )

        assert caplog.messages == ["Downloaded 512 bytes from https://x/y.png"]

    def test_renders_download_failed(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.ERROR, logger="test.uds"):
            adapter.error(
                "uds.image.download_failed",
                url="https://x/y.png",
                error="boom",
            )

        assert caplog.messages == [
            "Failed to download image from https://x/y.png: boom"
        ]

    def test_renders_presigned_upload_start(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug(
                "uds.image.presigned_upload_start", size=256, method="PUT"
            )

        assert caplog.messages == [
            "Uploading 256 bytes to presigned URL (method=PUT)"
        ]

    def test_renders_presigned_upload_done(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            adapter.debug("uds.image.presigned_upload_done", status=200)

        assert caplog.messages == ["Upload completed with status 200"]

    def test_renders_upload_failed(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))

        with caplog.at_level(logging.ERROR, logger="test.uds"):
            adapter.error("uds.image.upload_failed", error="boom")

        assert caplog.messages == ["Failed to upload image: boom"]

    def test_all_image_events_are_registered(self):
        from async_uds_api.log import _TEMPLATES

        expected_events = {
            "uds.image.upload_url_request",
            "uds.image.upload_url_received",
            "uds.image.upload_start_bytes",
            "uds.image.upload_start_source",
            "uds.image.read",
            "uds.image.uploaded",
            "uds.image.file_read_start",
            "uds.image.file_read_done",
            "uds.image.file_not_found",
            "uds.image.file_read_failed",
            "uds.image.download_start",
            "uds.image.download_done",
            "uds.image.download_failed",
            "uds.image.presigned_upload_start",
            "uds.image.presigned_upload_done",
            "uds.image.upload_failed",
        }

        registered = {
            key for key in _TEMPLATES if key.startswith("uds.image.")
        }

        assert registered == expected_events

    def test_no_image_event_falls_back_to_key_value(self, caplog):
        adapter = StdlibLoggerAdapter(logging.getLogger("test.uds"))
        fields_by_event = {
            "uds.image.upload_url_request": {"content_type": "image/png"},
            "uds.image.upload_url_received": {"image_id": "img-1"},
            "uds.image.upload_start_bytes": {
                "size": 1,
                "content_type": "image/png",
            },
            "uds.image.upload_start_source": {
                "source": "x",
                "content_type": "image/png",
            },
            "uds.image.read": {"size": 1},
            "uds.image.uploaded": {"image_id": "img-1"},
            "uds.image.file_read_start": {"path": "/tmp/x"},
            "uds.image.file_read_done": {"size": 1, "path": "/tmp/x"},
            "uds.image.file_not_found": {"path": "/tmp/x"},
            "uds.image.file_read_failed": {
                "path": "/tmp/x",
                "error": "boom",
            },
            "uds.image.download_start": {"url": "https://x"},
            "uds.image.download_done": {"size": 1, "url": "https://x"},
            "uds.image.download_failed": {
                "url": "https://x",
                "error": "boom",
            },
            "uds.image.presigned_upload_start": {
                "size": 1,
                "method": "PUT",
            },
            "uds.image.presigned_upload_done": {"status": 200},
            "uds.image.upload_failed": {"error": "boom"},
        }

        with caplog.at_level(logging.DEBUG, logger="test.uds"):
            for event, fields in fields_by_event.items():
                adapter.debug(event, **fields)

        assert len(caplog.messages) == len(fields_by_event)
        for message, event in zip(
            caplog.messages, fields_by_event, strict=True
        ):
            assert not message.startswith(event)


class TestPublicExports:
    def test_logging_helpers_are_exported(self):
        import typing

        import async_uds_api

        assert issubclass(async_uds_api.LoggerProtocol, typing.Protocol)
        for method_name in ("debug", "info", "warning", "error"):
            assert hasattr(async_uds_api.StdlibLoggerAdapter, method_name)
        assert async_uds_api.StdlibLoggerAdapter is not None
        assert async_uds_api.mask_value("+79991234567") == "***4567"
        assert async_uds_api.mask_params({"uid": "abcd1234"}) == {
            "uid": "***1234"
        }
        assert "phone" in async_uds_api.SENSITIVE_PARAMS
        assert not hasattr(async_uds_api, "redact_message")
        assert async_uds_api.mask_url("https://x/y.png?a=1") == "https://x/***"

    def test_get_logger_still_available(self):
        import logging

        import async_uds_api

        assert isinstance(async_uds_api.get_logger(), logging.Logger)


class TestMaskUrl:
    def test_masks_query_string(self):
        assert (
            mask_url("https://s3.example/img.png?X-Amz-Signature=abc")
            == "https://s3.example/***"
        )

    def test_masks_path_even_without_query(self):
        assert (
            mask_url("https://s3.example/img.png") == "https://s3.example/***"
        )

    def test_masks_multi_param_query_string(self):
        assert (
            mask_url(
                "https://s3.example/img.png?"
                "X-Amz-Signature=abc&X-Amz-Expires=60"
            )
            == "https://s3.example/***"
        )

    def test_masks_path_embedded_token(self):
        token = "".join(["DEAD", "BEEF", "SECRET"])
        masked = mask_url(f"https://bucket.s3.amazonaws.com/{token}/key.jpg")
        assert masked == "https://bucket.s3.amazonaws.com/***"
        assert token not in masked

    def test_drops_userinfo_entirely(self):
        password = "".join(["P4SS", "WORD", "XYZ"])
        masked = mask_url(
            f"https://user:{password}@bucket.example.com/k.jpg?sig=abc"
        )
        assert masked == "https://bucket.example.com/***"
        assert password not in masked
        assert "user" not in masked

    def test_drops_fragment(self):
        assert (
            mask_url("https://s3.example/img.png#secret")
            == "https://s3.example/***"
        )

    def test_keeps_non_default_port(self):
        assert (
            mask_url("https://cdn.example.com:8443/a/b?x=1")
            == "https://cdn.example.com:8443/***"
        )

    def test_drops_default_port(self):
        assert (
            mask_url("https://cdn.example.com:443/a/b")
            == "https://cdn.example.com/***"
        )
        assert (
            mask_url("http://cdn.example.com:80/a/b")
            == "http://cdn.example.com/***"
        )

    def test_uniform_output_for_empty_or_root_path(self):
        assert mask_url("https://host") == "https://host/***"
        assert mask_url("https://host/") == "https://host/***"

    def test_keeps_ipv6_host_bracketed(self):
        assert mask_url("https://[::1]:8443/a?b=1") == "https://[::1]:8443/***"

    def test_masks_url_with_unparseable_port(self):
        token = "".join(["SEC", "RET"])
        masked = mask_url(f"https://h:notaport/p?token={token}")
        assert masked == "https://***"
        assert token not in masked

    def test_masks_url_with_out_of_range_port(self):
        token = "".join(["SEC", "RET"])
        masked = mask_url(f"https://h:99999/p?token={token}")
        assert masked == "https://***"
        assert token not in masked

    def test_masks_url_with_empty_host(self):
        token = "".join(["SEC", "RET"])
        masked = mask_url(f"https:///p?token={token}")
        assert masked == "https://***"
        assert token not in masked

    @pytest.mark.parametrize(
        "value",
        [
            "",
            "://",
            "bareword",
            "/local/path/img.png",
            "./rel/what?ever.zzz",
            "C:\\images\\a.png",
            "ftp://host/p?q=1",
            "not a url at all",
        ],
    )
    def test_returns_non_http_url_input_unchanged(self, value):
        assert mask_url(value) == value

    @pytest.mark.parametrize(
        ("value", "expected"),
        [
            ("https://", "https://***"),
            ("http://", "http://***"),
            ("https://[bad", "***"),
            ("https://host:notaport/a", "https://***"),
        ],
    )
    def test_malformed_http_url_never_round_trips(self, value, expected):
        assert mask_url(value) == expected


class BrokenHandler(logging.Handler):
    def __init__(self):
        super().__init__()
        self.attempts = 0

    def emit(self, record):
        self.attempts += 1
        raise RuntimeError("handler boom")


@pytest.fixture
def broken_handler_logger(request):
    logger = logging.getLogger(request.param)
    handler = BrokenHandler()
    original_level = logger.level
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    yield logger, handler
    logger.removeHandler(handler)
    logger.setLevel(original_level)


class TestStdlibLoggerAdapterDebugEscapeHatch:
    @pytest.mark.parametrize(
        "broken_handler_logger",
        ["test.uds.escape_hatch.default"],
        indirect=True,
    )
    def test_swallows_broken_handler_by_default(
        self, broken_handler_logger, monkeypatch
    ):
        monkeypatch.delenv("ASYNC_UDS_API_DEBUG_LOGGING", raising=False)
        logger, handler = broken_handler_logger
        adapter = StdlibLoggerAdapter(logger)

        adapter.info("uds.request", method="GET", path="/x")

        assert handler.attempts == 1

    @pytest.mark.parametrize(
        "broken_handler_logger",
        ["test.uds.escape_hatch.enabled"],
        indirect=True,
    )
    def test_reraises_when_debug_env_var_set(
        self, broken_handler_logger, monkeypatch
    ):
        monkeypatch.setenv("ASYNC_UDS_API_DEBUG_LOGGING", "1")
        logger, _ = broken_handler_logger
        adapter = StdlibLoggerAdapter(logger)

        with pytest.raises(RuntimeError, match="handler boom"):
            adapter.info("uds.request", method="GET", path="/x")
