from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Type

import httpx

from .errors import (
    UDSAPIError,
    UDSBadRequestError,
    UDSForbiddenError,
    UDSNotFoundError,
    UDSUnauthorizedError,
    UDSUnexpectedError,
)
from .models import (
    CompanySettings,
    CreateOperation,
    CustomerDetail,
    CustomersPage,
    OperationsPage,
    PurchaseCalcRequest,
    PurchaseCalcResponse,
    RefundOperationRequest,
    RewardRequest,
    Operation,
)


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

        # Под-клиенты для структурированного доступа к API
        self.settings = _SettingsAPI(self)
        self.customers = _CustomersAPI(self)
        self.operations = _OperationsAPI(self)

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
        except httpx.HTTPStatusError as exc:  # pragma: no cover - тонкая обвязка
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
                # тело не JSON — оставляем message как есть
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

            raise exc_cls(message, status_code=status, error_code=error_code) from exc

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

    async def get_settings(self) -> CompanySettings:
        """
        Получить настройки компании (GET /settings).
        """
        return await self.settings.get()

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

        return await self.customers.list(max=max, offset=offset, cursor=cursor)

    async def find_customer(
        self,
        *,
        code: Optional[str] = None,
        phone: Optional[str] = None,
        uid: Optional[str] = None,
        exchange_code: Optional[bool] = None,
        total: Optional[float] = None,
        skip_loyalty_total: Optional[float] = None,
        unredeemable_total: Optional[float] = None,
    ) -> PurchaseCalcResponse:
        """
        Найти клиента по коду, телефону или UID (GET /customers/find).
        """
        params: Dict[str, Any] = {}
        if code is not None:
            params["code"] = code
        if phone is not None:
            params["phone"] = phone
        if uid is not None:
            params["uid"] = uid
        if exchange_code is not None:
            params["exchangeCode"] = exchange_code
        if total is not None:
            params["total"] = total
        if skip_loyalty_total is not None:
            params["skipLoyaltyTotal"] = skip_loyalty_total
        if unredeemable_total is not None:
            params["unredeemableTotal"] = unredeemable_total

        return await self.customers.find(
            code=code,
            phone=phone,
            uid=uid,
            exchange_code=exchange_code,
            total=total,
            skip_loyalty_total=skip_loyalty_total,
            unredeemable_total=unredeemable_total,
        )

    async def get_customer(self, customer_id: int) -> CustomerDetail:
        """
        Получить подробную информацию о клиенте (GET /customers/{id}).
        """
        return await self.customers.get(customer_id)

    async def list_operations(
        self,
        *,
        max: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OperationsPage:
        """
        Получить список транзакций (GET /operations).
        """
        params: Dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        return await self.operations.list(max=max, offset=offset, cursor=cursor)

    async def create_operation(self, operation: CreateOperation) -> Operation:
        """
        Создать транзакцию (POST /operations).
        """
        return await self.operations.create(operation)

    async def get_operation(self, operation_id: int) -> Operation:
        """
        Получить информацию о транзакции (GET /operations/{id}).
        """
        return await self.operations.get(operation_id)

    async def refund_operation(
        self,
        operation_id: int,
        refund: Optional[RefundOperationRequest] = None,
    ) -> Operation:
        """
        Вернуть транзакцию полностью или частично (POST /operations/{id}/refund).
        """
        return await self.operations.refund(operation_id, refund)

    async def calc_purchase(
        self,
        calc_request: PurchaseCalcRequest,
    ) -> PurchaseCalcResponse:
        """
        Рассчитать параметры операции (POST /operations/calc).
        """
        return await self.operations.calc(calc_request)

    async def reward(
        self,
        reward_request: RewardRequest,
    ) -> None:
        """
        Начислить пользователям баллы (подарок) (POST /operations/reward).
        """
        await self.operations.reward(reward_request)


class _SettingsAPI:
    def __init__(self, client: UDSClient) -> None:
        self._client = client

    async def get(self) -> CompanySettings:
        data = await self._client._get_json("/settings")
        return CompanySettings.model_validate(data)


class _CustomersAPI:
    def __init__(self, client: UDSClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        max: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> CustomersPage:
        params: Dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        data = await self._client._get_json("/customers", params=params or None)
        return CustomersPage.model_validate(data)

    async def find(
        self,
        *,
        code: Optional[str] = None,
        phone: Optional[str] = None,
        uid: Optional[str] = None,
        exchange_code: Optional[bool] = None,
        total: Optional[float] = None,
        skip_loyalty_total: Optional[float] = None,
        unredeemable_total: Optional[float] = None,
    ) -> PurchaseCalcResponse:
        params: Dict[str, Any] = {}
        if code is not None:
            params["code"] = code
        if phone is not None:
            params["phone"] = phone
        if uid is not None:
            params["uid"] = uid
        if exchange_code is not None:
            params["exchangeCode"] = exchange_code
        if total is not None:
            params["total"] = total
        if skip_loyalty_total is not None:
            params["skipLoyaltyTotal"] = skip_loyalty_total
        if unredeemable_total is not None:
            params["unredeemableTotal"] = unredeemable_total

        data = await self._client._get_json("/customers/find", params=params or None)
        return PurchaseCalcResponse.model_validate(data)

    async def get(self, customer_id: int) -> CustomerDetail:
        data = await self._client._get_json(f"/customers/{customer_id}")
        return CustomerDetail.model_validate(data)


class _OperationsAPI:
    def __init__(self, client: UDSClient) -> None:
        self._client = client

    async def list(
        self,
        *,
        max: Optional[int] = None,
        offset: Optional[int] = None,
        cursor: Optional[str] = None,
    ) -> OperationsPage:
        params: Dict[str, Any] = {}
        if max is not None:
            params["max"] = max
        if offset is not None:
            params["offset"] = offset
        if cursor is not None:
            params["cursor"] = cursor

        data = await self._client._get_json("/operations", params=params or None)
        return OperationsPage.model_validate(data)

    async def create(self, operation: CreateOperation) -> Operation:
        body = operation.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json("/operations", body=body)
        return Operation.model_validate(data)

    async def get(self, operation_id: int) -> Operation:
        data = await self._client._get_json(f"/operations/{operation_id}")
        return Operation.model_validate(data)

    async def refund(
        self,
        operation_id: int,
        refund: Optional[RefundOperationRequest] = None,
    ) -> Operation:
        body = refund.model_dump(by_alias=True, exclude_none=True) if refund else None
        data = await self._client._post_json(
            f"/operations/{operation_id}/refund",
            body=body,
        )
        return Operation.model_validate(data) if data else Operation()

    async def calc(
        self,
        calc_request: PurchaseCalcRequest,
    ) -> PurchaseCalcResponse:
        body = calc_request.model_dump(by_alias=True, exclude_none=True)
        data = await self._client._post_json("/operations/calc", body=body)
        return PurchaseCalcResponse.model_validate(data)

    async def reward(
        self,
        reward_request: RewardRequest,
    ) -> None:
        body = reward_request.model_dump(by_alias=True, exclude_none=True)
        await self._client._post_json("/operations/reward", body=body)


