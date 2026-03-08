from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type

import httpx

from .api import CustomersAPI, OperationsAPI, SettingsAPI, TagsAPI
from .errors import (
    UDSAPIError,
    UDSBadRequestError,
    UDSForbiddenError,
    UDSNotFoundError,
    UDSUnauthorizedError,
    UDSUnexpectedError,
)

DEFAULT_BASE_URL = "https://api.uds.app/partner/v2"


class UDSClient:
    """
    Асинхронный клиент для UDS Partner API v2.

    Поддерживает:
    - базовую авторизацию (companyId:apiKey);
    - автоматическую установку заголовков X-Origin-Request-Id и X-Timestamp.

    Доступ к API через атрибуты:
    - settings: SettingsAPI
    - customers: CustomersAPI
    - operations: OperationsAPI
    - tags: TagsAPI
    """

    def __init__(
        self,
        company_id: int,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = 10.0,
        client: Optional[httpx.AsyncClient] = None,
    ) -> None:
        self._company_id = company_id
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._external_client = client is not None
        self._client: httpx.AsyncClient = client or httpx.AsyncClient(
            base_url=self._base_url,
            timeout=self._timeout,
        )

        self.settings = SettingsAPI(self)
        self.customers = CustomersAPI(self)
        self.operations = OperationsAPI(self)
        self.tags = TagsAPI(self)

    async def aclose(self) -> None:
        if not self._external_client:
            await self._client.aclose()

    async def __aenter__(self) -> "UDSClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    def _build_headers(self) -> Dict[str, str]:
        now = datetime.now(timezone.utc).isoformat()
        return {
            "Accept": "application/json",
            "Accept-Charset": "utf-8",
            "X-Origin-Request-Id": str(uuid.uuid4()),
            "X-Timestamp": now,
        }

    def _build_auth(self) -> httpx.BasicAuth:
        return httpx.BasicAuth(str(self._company_id), self._api_key)

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        try:
            response = await self._client.request(
                method=method,
                url=path,
                params=params,
                json=json,
                headers=self._build_headers(),
                auth=self._build_auth(),
            )
            response.raise_for_status()
            return response
        except (
            httpx.HTTPStatusError
        ) as exc:
            res = exc.response
            status = res.status_code
            error_code: Optional[str] = None
            message: str = res.text

            try:
                payload = res.json()
                if isinstance(payload, dict):
                    error_code = payload.get("errorCode") or error_code
                    message = payload.get("message") or message
            except Exception:
                pass

            exc_cls: Type[UDSAPIError]
            if status == 400:
                exc_cls = UDSBadRequestError
            elif status == 401:
                exc_cls = UDSUnauthorizedError
            elif status == 403:
                exc_cls = UDSForbiddenError
            elif status == 404:
                exc_cls = UDSNotFoundError
            else:
                exc_cls = UDSUnexpectedError

            raise exc_cls(
                message, status_code=status, error_code=error_code
            ) from exc

    async def _get_json(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = await self._request("GET", path, params=params)
        data = response.json()
        assert isinstance(data, dict)
        return data

    async def _post_json(
        self,
        path: str,
        *,
        body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        response = await self._request("POST", path, params=params, json=body)
        if response.content:
            data = response.json()
            assert isinstance(data, dict)
            return data
        return {}
