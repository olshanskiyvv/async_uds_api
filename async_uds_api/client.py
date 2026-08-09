from __future__ import annotations

import hashlib
import hmac
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import httpx
from tenacity import (
    AsyncRetrying,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from async_uds_api.api import (
    CustomersAPI,
    GoodsAPI,
    GoodsOrdersAPI,
    ImagesAPI,
    OperationsAPI,
    SettingsAPI,
    TagsAPI,
)
from async_uds_api.errors import (
    UDSAPIError,
    UDSBadRequestError,
    UDSClientError,
    UDSForbiddenError,
    UDSNotFoundError,
    UDSRateLimitError,
    UDSServerError,
    UDSUnauthorizedError,
    UDSUnexpectedError,
)
from async_uds_api.log import (
    LoggerProtocol,
    StdlibLoggerAdapter,
    mask_params,
)
from async_uds_api.request_id import get_origin_request_id

DEFAULT_BASE_URL = "https://api.uds.app/partner/v2"


class UDSClient:
    """
    Асинхронный клиент для UDS Partner API v2.

    Поддерживает:
    - базовую авторизацию (companyId:apiKey);
    - автоматическую установку заголовков X-Origin-Request-Id и X-Timestamp;
    - передачу внешнего идентификатора цепочки запросов в
      X-Origin-Request-Id: через параметр request_id любого метода API,
      через use_origin_request_id или через set_origin_request_id.
      Значение уходит в заголовок как есть и не валидируется.

    Доступ к API через атрибуты:
    - settings: SettingsAPI
    - customers: CustomersAPI
    - operations: OperationsAPI
    - tags: TagsAPI
    - goods: GoodsAPI
    - images: ImagesAPI

    Параметры логирования:
    - logger: объект с методами debug/info/warning/error, принимающими
      (event: str, **fields). Подходят structlog и loguru. По умолчанию
      используется StdlibLoggerAdapter поверх
      logging.getLogger("async_uds_api"), который сохраняет классический
      формат сообщений.
    - silence_httpx_log: при True (по умолчанию) логгеру "httpx" выставляется
      уровень WARNING. ВНИМАНИЕ: при False httpx логирует полный URL запроса
      вместе с query-строкой, включая незамаскированные phone, uid и code.
    """

    def __init__(
        self,
        company_id: str,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        retries: int = 3,
        limits: httpx.Limits | None = None,
        settings_ttl: float = 60.0,
        client: httpx.AsyncClient | None = None,
        logger: LoggerProtocol | None = None,
        silence_httpx_log: bool = True,
    ) -> None:
        if not company_id or not company_id.strip():
            raise ValueError("company_id cannot be empty")
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")

        self._company_id = company_id
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._retries = retries
        self._external_client = client is not None
        if isinstance(logger, (logging.Logger, logging.LoggerAdapter)):
            self._logger: LoggerProtocol = StdlibLoggerAdapter(logger)
        elif logger is None:
            self._logger = StdlibLoggerAdapter(
                logging.getLogger("async_uds_api")
            )
        else:
            missing = [
                name
                for name in ("debug", "info", "warning", "error")
                if not callable(getattr(logger, name, None))
            ]
            if missing:
                raise TypeError(
                    "logger is missing required method(s): "
                    + ", ".join(missing)
                )
            self._logger = logger
        if silence_httpx_log:
            logging.getLogger("httpx").setLevel(logging.WARNING)
        self._client: httpx.AsyncClient = client or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
            limits=limits
            or httpx.Limits(
                max_connections=100,
                max_keepalive_connections=20,
            ),
        )
        self._auth = httpx.BasicAuth(company_id, api_key)

        self.settings = SettingsAPI(self, ttl=settings_ttl)
        self.customers = CustomersAPI(self)
        self.operations = OperationsAPI(self)
        self.tags = TagsAPI(self)
        self.goods = GoodsAPI(self)
        self.images = ImagesAPI(self, timeout=self._timeout)
        self.goods_orders = GoodsOrdersAPI(self)

    def __repr__(self) -> str:
        masked = self._api_key[:4] + "***" if len(self._api_key) > 4 else "***"
        return (
            f"UDSClient(company_id={self._company_id!r}, api_key='{masked}')"
        )

    async def aclose(self) -> None:
        if not self._external_client:
            await self._client.aclose()

        await self.images.aclose()

    async def __aenter__(self) -> UDSClient:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: object,
    ) -> None:
        await self.aclose()

    def _build_headers(self, request_id: str | None = None) -> dict[str, str]:
        now = datetime.now(timezone.utc).isoformat()
        resolved = request_id or get_origin_request_id() or str(uuid.uuid4())
        return {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-Origin-Request-Id": resolved,
            "X-Timestamp": now,
        }

    def _build_auth(self) -> httpx.BasicAuth:
        return self._auth

    def verify_webhook_signature(
        self,
        request_id: str,
        timestamp: str,
        signature: str,
    ) -> bool:
        """
        Verify webhook X-Signature header.

        Signature = md5(concat(X-RequestId, X-Timestamp, Client-Id, Api-Key))
        """
        concatenated = (
            f"{request_id}{timestamp}{self._company_id}{self._api_key}"
        )
        expected_signature = hashlib.md5(concatenated.encode()).hexdigest()
        return hmac.compare_digest(expected_signature, signature)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> httpx.Response:
        async for attempt in AsyncRetrying(
            retry=retry_if_exception_type(
                (UDSRateLimitError, UDSServerError, httpx.TransportError)
            ),
            stop=stop_after_attempt(self._retries),
            wait=wait_exponential(multiplier=1, min=1, max=10),
            reraise=True,
        ):
            with attempt:
                if attempt.retry_state.attempt_number > 1:
                    self._logger.warning(
                        "uds.retry",
                        method=method,
                        path=path,
                        attempt=attempt.retry_state.attempt_number,
                    )
                return await self._do_request(
                    method,
                    path,
                    params=params,
                    json=json,
                    request_id=request_id,
                )
        raise UDSClientError("Retry loop exited unexpectedly")

    async def _do_request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> httpx.Response:
        headers = self._build_headers(request_id)
        origin_request_id = headers["X-Origin-Request-Id"]
        timestamp = headers["X-Timestamp"]

        self._logger.info(
            "uds.request",
            method=method,
            path=path,
            params=mask_params(params),
            request_id=origin_request_id,
            timestamp=timestamp,
        )

        start_time = time.monotonic()
        try:
            response = await self._client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                headers=headers,
                auth=self._build_auth(),
            )
            response.raise_for_status()

            elapsed = time.monotonic() - start_time
            self._logger.info(
                "uds.response",
                method=method,
                path=path,
                status=response.status_code,
                elapsed=elapsed,
                request_id=origin_request_id,
                uds_request_id=response.headers.get("X-Request-Id"),
            )
            return response
        except httpx.HTTPStatusError as exc:
            elapsed = time.monotonic() - start_time
            res = exc.response
            status = res.status_code
            error_code: str | None = None
            message: str | None = None

            try:
                payload = res.json()
                if isinstance(payload, dict):
                    error_code = payload.get("errorCode") or error_code
                    raw_message = payload.get("message")
                    if isinstance(raw_message, str):
                        message = raw_message or None
            except Exception:
                pass

            if not message or not message.strip():
                message = f"{status} for {method} {path}"

            self._logger.error(
                "uds.error",
                method=method,
                path=path,
                status=status,
                elapsed=elapsed,
                error_code=error_code,
                request_id=origin_request_id,
                uds_request_id=res.headers.get("X-Request-Id"),
            )

            exc_cls: type[UDSAPIError]
            if status == 400:
                exc_cls = UDSBadRequestError
            elif status == 401:
                exc_cls = UDSUnauthorizedError
            elif status == 403:
                exc_cls = UDSForbiddenError
            elif status == 404:
                exc_cls = UDSNotFoundError
            elif status == 429:
                exc_cls = UDSRateLimitError
            elif status >= 500:
                exc_cls = UDSServerError
            else:
                exc_cls = UDSUnexpectedError

            exc.args = (f"{status} for {method} {path}",)
            raise exc_cls(
                message,
                status_code=status,
                error_code=error_code,
                method=method,
                path=path,
            ) from exc

    async def _get_json(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        response = await self._request(
            "GET", path, params=params, request_id=request_id
        )
        data = response.json()
        if not isinstance(data, dict):
            raise UDSClientError(
                "Unexpected API response shape: expected dict"
            )
        return data

    async def _post_json(
        self,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        response = await self._request(
            "POST", path, params=params, json=body, request_id=request_id
        )
        if response.content:
            data = response.json()
            if not isinstance(data, dict):
                raise UDSClientError(
                    "Unexpected API response shape: expected dict"
                )
            return data
        return {}

    async def _put_json(
        self,
        path: str,
        *,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> dict[str, Any]:
        response = await self._request(
            "PUT", path, params=params, json=body, request_id=request_id
        )
        if response.content:
            data = response.json()
            if not isinstance(data, dict):
                raise UDSClientError(
                    "Unexpected API response shape: expected dict"
                )
            return data
        return {}

    async def _delete(
        self,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        request_id: str | None = None,
    ) -> None:
        await self._request(
            "DELETE", path, params=params, request_id=request_id
        )
