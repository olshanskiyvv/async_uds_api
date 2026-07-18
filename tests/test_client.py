import logging
import traceback

import httpx
import pytest
import respx

from async_uds_api import UDSClient
from async_uds_api.log import StdlibLoggerAdapter


def formatted_traceback(exc: BaseException) -> str:
    """Render the exception exactly as logging.exception would."""
    return "".join(
        traceback.format_exception(type(exc), exc, exc.__traceback__)
    )


class TestUDSClient:
    def test_client_initialization(self):
        """Test UDSClient initialization."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
        )

        assert client._company_id == "123456"
        assert client._api_key == "test-api-key"
        assert client._base_url == "https://api.uds.app/partner/v2"

    def test_client_default_values(self):
        """Test UDSClient default values."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
        )

        assert client._timeout == 10.0
        assert client._external_client is False

    def test_client_custom_base_url(self):
        """Test UDSClient with custom base URL."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
            base_url="https://custom.api.com/v1",
        )

        assert client._base_url == "https://custom.api.com/v1"

    def test_client_custom_timeout(self):
        """Test UDSClient with custom timeout."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
            timeout=30.0,
        )

        assert client._timeout == 30.0

    async def test_client_context_manager(self):
        """Test UDSClient as async context manager."""
        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
        ) as client:
            assert client is not None
            assert isinstance(client, UDSClient)

    def test_client_build_headers(self):
        """Test UDSClient header generation."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
        )

        headers = client._build_headers()

        assert "Accept" in headers
        assert headers["Accept"] == "application/json"
        assert "X-Origin-Request-Id" in headers
        assert "X-Timestamp" in headers

    def test_client_build_auth(self):
        """Test UDSClient basic auth generation."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
        )

        auth = client._build_auth()

        assert isinstance(auth, httpx.BasicAuth)

    def test_client_api_attributes(self):
        """Test UDSClient has all API attributes."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
        )

        assert hasattr(client, "settings")
        assert hasattr(client, "customers")
        assert hasattr(client, "operations")
        assert hasattr(client, "tags")
        assert hasattr(client, "goods")
        assert hasattr(client, "images")

    async def test_client_close(self):
        """Test UDSClient close method."""
        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
        )

        await client.aclose()

    async def test_client_with_external_httpx_client(self):
        """Test UDSClient with external httpx.AsyncClient."""
        external_client = httpx.AsyncClient(
            base_url="https://api.uds.app/partner/v2",
        )

        client = UDSClient(
            company_id="123456",
            api_key="test-api-key",
            client=external_client,
        )

        assert client._external_client is True

        await client.aclose()
        await external_client.aclose()

    def test_client_repr_masks_api_key(self):
        client = UDSClient(company_id="123456", api_key="secret-key-xyz")
        r = repr(client)
        assert "123456" in r
        assert "secr***" in r
        assert "secret-key-xyz" not in r

    def test_client_repr_short_api_key(self):
        client = UDSClient(company_id="123456", api_key="abc")
        assert "***" in repr(client)
        assert "abc" not in repr(client)

    def test_client_empty_company_id(self):
        """Test that empty company_id raises ValueError."""
        with pytest.raises(ValueError, match="company_id cannot be empty"):
            UDSClient(company_id="", api_key="test-key")

        with pytest.raises(ValueError, match="company_id cannot be empty"):
            UDSClient(company_id="   ", api_key="test-key")

    def test_client_empty_api_key(self):
        """Test that empty api_key raises ValueError."""
        with pytest.raises(ValueError, match="api_key cannot be empty"):
            UDSClient(company_id="123456", api_key="")

        with pytest.raises(ValueError, match="api_key cannot be empty"):
            UDSClient(company_id="123456", api_key="   ")


class FakeLogger:
    def __init__(self):
        self.events = []

    def debug(self, event, **fields):
        self.events.append(("debug", event, fields))

    def info(self, event, **fields):
        self.events.append(("info", event, fields))

    def warning(self, event, **fields):
        self.events.append(("warning", event, fields))

    def error(self, event, **fields):
        self.events.append(("error", event, fields))


@pytest.fixture
def httpx_log_level():
    logger = logging.getLogger("httpx")
    original = logger.level
    yield logger
    logger.setLevel(original)


class TestClientLogging:
    def test_default_logger_is_stdlib_adapter(self):
        client = UDSClient(company_id="123456", api_key="test-api-key")

        assert isinstance(client._logger, StdlibLoggerAdapter)

    def test_custom_logger_is_used(self):
        fake = FakeLogger()

        client = UDSClient(
            company_id="123456", api_key="test-api-key", logger=fake
        )

        assert client._logger is fake

    def test_plain_stdlib_logger_is_wrapped(self):
        raw_logger = logging.getLogger("some.logger")

        client = UDSClient(
            company_id="123456", api_key="test-api-key", logger=raw_logger
        )

        assert isinstance(client._logger, StdlibLoggerAdapter)
        assert client._logger._logger is raw_logger

    def test_logger_adapter_is_wrapped(self):
        raw_adapter = logging.LoggerAdapter(
            logging.getLogger("some.adapter.logger"), {}
        )

        client = UDSClient(
            company_id="123456", api_key="test-api-key", logger=raw_adapter
        )

        assert isinstance(client._logger, StdlibLoggerAdapter)
        assert client._logger._logger is raw_adapter

    async def test_logger_adapter_survives_real_request_at_info_level(
        self, mock_httpx, caplog
    ):
        raw_adapter = logging.LoggerAdapter(
            logging.getLogger("some.adapter.request"), {}
        )
        respx.get("https://api.uds.app/partner/v2/customers").mock(
            return_value=httpx.Response(200, json={"rows": []})
        )

        with caplog.at_level(logging.INFO, logger="some.adapter.request"):
            async with UDSClient(
                company_id="123456",
                api_key="test-api-key",
                retries=1,
                logger=raw_adapter,
            ) as client:
                await client._get_json("/customers")

    def test_non_logger_object_missing_methods_raises_type_error(self):
        with pytest.raises(TypeError):
            UDSClient(
                company_id="123456", api_key="test-api-key", logger=object()
            )

    def test_valid_duck_typed_logger_is_still_accepted(self):
        fake = FakeLogger()

        client = UDSClient(
            company_id="123456", api_key="test-api-key", logger=fake
        )

        assert client._logger is fake

    def test_silences_httpx_logger_by_default(self, httpx_log_level):
        httpx_log_level.setLevel(logging.INFO)

        UDSClient(company_id="123456", api_key="test-api-key")

        assert httpx_log_level.level == logging.WARNING

    def test_leaves_httpx_logger_alone_when_disabled(self, httpx_log_level):
        httpx_log_level.setLevel(logging.INFO)

        UDSClient(
            company_id="123456",
            api_key="test-api-key",
            silence_httpx_log=False,
        )

        assert httpx_log_level.level == logging.INFO

    async def test_request_event_masks_sensitive_params(self, mock_httpx):
        fake = FakeLogger()
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(200, json={"user": None})
        )

        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            logger=fake,
        ) as client:
            await client._get_json(
                "/customers/find", params={"phone": "+79991234567"}
            )

        request_events = [e for e in fake.events if e[1] == "uds.request"]
        assert request_events[0][2]["params"] == {"phone": "***4567"}

    async def test_phone_never_appears_in_stdlib_output(
        self, mock_httpx, caplog
    ):
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(200, json={"user": None})
        )

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                await client._get_json(
                    "/customers/find", params={"phone": "+79991234567"}
                )

        assert "+79991234567" not in caplog.text
        assert "79991234567" not in caplog.text

    async def test_response_event_reports_status(self, mock_httpx):
        fake = FakeLogger()
        respx.get("https://api.uds.app/partner/v2/customers").mock(
            return_value=httpx.Response(200, json={"rows": []})
        )

        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            logger=fake,
        ) as client:
            await client._get_json("/customers")

        response_events = [e for e in fake.events if e[1] == "uds.response"]
        assert response_events[0][2]["status"] == 200

    async def test_exception_chain_does_not_leak_phone(self, mock_httpx):
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(404, json={"message": "Not found"})
        )

        phone = "+79991234567"

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=1
        ) as client:
            with pytest.raises(Exception) as exc_info:
                await client._get_json(
                    "/customers/find", params={"phone": phone}
                )

        cause = exc_info.value.__cause__
        assert cause is not None
        chain_text = "".join(
            traceback.format_exception_only(
                type(exc_info.value), exc_info.value
            )
        ) + "".join(traceback.format_exception_only(type(cause), cause))
        assert "79991234567" not in chain_text
        assert "79991234567" not in formatted_traceback(exc_info.value)

    async def test_error_event_emitted_with_fields(self, mock_httpx):
        fake = FakeLogger()
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(
                404,
                json={"errorCode": "notFound", "message": "Not found"},
            )
        )

        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            logger=fake,
        ) as client:
            with pytest.raises(Exception):
                await client._get_json(
                    "/customers/find", params={"phone": "+79991234567"}
                )

        error_events = [e for e in fake.events if e[1] == "uds.error"]
        assert len(error_events) == 1
        fields = error_events[0][2]
        for key in ("method", "path", "status", "elapsed", "error_code"):
            assert key in fields
        assert "message" not in fields
        assert fields["status"] == 404
        assert fields["error_code"] == "notFound"

    async def test_retry_event_emitted_with_fields(self, mock_httpx):
        fake = FakeLogger()
        route = respx.get("https://api.uds.app/partner/v2/customers")
        route.side_effect = [
            httpx.Response(500, json={"message": "Server error"}),
            httpx.Response(200, json={"rows": []}),
        ]

        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=2,
            logger=fake,
        ) as client:
            await client._get_json("/customers")

        retry_events = [e for e in fake.events if e[1] == "uds.retry"]
        assert len(retry_events) == 1
        fields = retry_events[0][2]
        assert fields["method"] == "GET"
        assert fields["path"] == "/customers"
        assert fields["attempt"] == 2


class TestServerMessageContainment:
    async def test_phone_echo_never_reaches_log_or_exception(
        self, mock_httpx, caplog
    ):
        fake = FakeLogger()
        phone = "+79991234567"
        server_message = (
            "Customer 79991234567 / +7 (999) 123-45-67 / "
            "+7-999-123-45-67 not found"
        )
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(
                400,
                json={"errorCode": "badRequest", "message": server_message},
            )
        )

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456",
                api_key="test-api-key",
                retries=1,
                logger=fake,
            ) as client:
                with pytest.raises(Exception) as exc_info:
                    await client._get_json(
                        "/customers/find", params={"phone": phone}
                    )

        leaks = ("79991234567", "9991234567", "123-45-67", "123 45 67")
        error_fields = [e[2] for e in fake.events if e[1] == "uds.error"][0]
        rendered_fields = " ".join(str(v) for v in error_fields.values())
        tb_text = formatted_traceback(exc_info.value)
        for leak in leaks:
            assert leak not in caplog.text
            assert leak not in rendered_fields
            assert leak not in str(exc_info.value)
            assert leak not in tb_text
        assert "message" not in error_fields
        assert exc_info.value.message == server_message

    async def test_uid_echo_never_reaches_log_or_exception(
        self, mock_httpx, caplog
    ):
        uid = "550e8400-e29b-41d4-a716-446655440000"
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(
                400,
                json={
                    "errorCode": "badRequest",
                    "message": f"Customer {uid} is blocked",
                },
            )
        )

        with caplog.at_level(logging.DEBUG, logger="async_uds_api"):
            async with UDSClient(
                company_id="123456", api_key="test-api-key", retries=1
            ) as client:
                with pytest.raises(Exception) as exc_info:
                    await client._get_json(
                        "/customers/find", params={"uid": uid}
                    )

        assert uid not in caplog.text
        assert uid not in str(exc_info.value)
        assert uid not in formatted_traceback(exc_info.value)
        assert uid in exc_info.value.message

    async def test_error_summary_contains_only_safe_parts(self, mock_httpx):
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(
                400,
                json={"errorCode": "badRequest", "message": "secret text"},
            )
        )

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=1
        ) as client:
            with pytest.raises(Exception) as exc_info:
                await client._get_json("/customers/find")

        text = str(exc_info.value)
        assert "secret text" not in text
        assert "400" in text
        assert "GET" in text
        assert "/customers/find" in text
        assert "badRequest" in text

    async def test_message_falls_back_to_summary_on_empty_body(
        self, mock_httpx
    ):
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(500)
        )

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=1
        ) as client:
            with pytest.raises(Exception) as exc_info:
                await client._get_json("/customers/find")

        assert exc_info.value.message == "500 for GET /customers/find"

    async def test_message_falls_back_to_summary_on_blank_body(
        self, mock_httpx
    ):
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(503, text="   \n")
        )

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=1
        ) as client:
            with pytest.raises(Exception) as exc_info:
                await client._get_json("/customers/find")

        assert exc_info.value.message == "503 for GET /customers/find"

    async def test_message_uses_plain_text_body(self, mock_httpx):
        respx.get("https://api.uds.app/partner/v2/customers/find").mock(
            return_value=httpx.Response(400, text="Bad Request: try again")
        )

        async with UDSClient(
            company_id="123456", api_key="test-api-key", retries=1
        ) as client:
            with pytest.raises(Exception) as exc_info:
                await client._get_json("/customers/find")

        assert exc_info.value.message == "Bad Request: try again"
        assert "Bad Request: try again" not in str(exc_info.value)


class TestLoggerGuard:
    async def test_broken_is_enabled_for_does_not_break_request(
        self, mock_httpx
    ):
        class BrokenAdapter(logging.LoggerAdapter):
            def isEnabledFor(self, level):  # noqa: N802
                raise RuntimeError("isEnabledFor boom")

        respx.get("https://api.uds.app/partner/v2/customers").mock(
            return_value=httpx.Response(200, json={"rows": []})
        )

        async with UDSClient(
            company_id="123456",
            api_key="test-api-key",
            retries=1,
            logger=BrokenAdapter(logging.getLogger("test.uds.broken2"), {}),
        ) as client:
            data = await client._get_json("/customers")

        assert data == {"rows": []}
