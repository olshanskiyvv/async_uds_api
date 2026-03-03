from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import httpx

from .models import CompanySettings, CustomersPage


DEFAULT_BASE_URL = "https://api.uds.app/partner/v2"


class UDSClient:
    """
    Асинхронный клиент для UDS Partner API v2.

    Поддерживает:
    - базовую авторизацию (companyId:apiKey);
    - автоматическую установку заголовков X-Origin-Request-Id и X-Timestamp;
    - методы:
        * get_settings -> GET /settings
        * list_customers -> GET /customers
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

    async def aclose(self) -> None:
        if not self._external_client:
            await self._client.aclose()

    async def __aenter__(self) -> "UDSClient":
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:  # type: ignore[override]
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

    async def _get(
        self,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        response = await self._client.get(
            url=path,
            params=params,
            headers=self._build_headers(),
            auth=self._build_auth(),
        )
        response.raise_for_status()
        return response

    async def get_settings(self) -> CompanySettings:
        """
        Получить настройки компании (GET /settings).
        """
        response = await self._get("/settings")
        data = response.json()
        return CompanySettings.model_validate(data)

    async def list_customers(
        self,
        *,
        max: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> CustomersPage:
        """
        Получить список клиентов (GET /customers).
        """
        params: Dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        response = await self._get("/customers", params=params or None)
        data = response.json()
        return CustomersPage.model_validate(data)

