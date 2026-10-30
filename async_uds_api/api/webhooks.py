"""Webhook helpers: signature verification and payload parsing."""

from __future__ import annotations

import hashlib
import hmac
import json
from typing import Any

from async_uds_api.models import Customer, GoodsOrderDetailed, Operation


class WebhooksAPI:
    """Webhook signature verification and payload parsing."""

    def __init__(self, company_id: str, api_key: str) -> None:
        self._company_id = company_id
        self._api_key = api_key

    def verify_signature(
        self,
        request_id: str,
        timestamp: str,
        signature: str,
    ) -> bool:
        """Verify the webhook ``X-Signature`` header.

        Signature = md5(concat(X-RequestId, X-Timestamp, companyId, apiKey)).
        """
        concatenated = (
            f"{request_id}{timestamp}{self._company_id}{self._api_key}"
        )
        expected = hashlib.md5(concatenated.encode()).hexdigest()
        return hmac.compare_digest(expected, signature)

    def parse_participant(self, payload: dict[str, Any] | str) -> Customer:
        """Parse a participant webhook payload into Customer."""
        return Customer.model_validate(self._load(payload))

    def parse_operation(self, payload: dict[str, Any] | str) -> Operation:
        """Parse an operation webhook payload into Operation."""
        return Operation.model_validate(self._load(payload))

    def parse_goods_order(
        self, payload: dict[str, Any] | str
    ) -> GoodsOrderDetailed:
        """Parse a goods-order webhook payload into GoodsOrderDetailed."""
        return GoodsOrderDetailed.model_validate(self._load(payload))

    @staticmethod
    def _load(payload: dict[str, Any] | str) -> Any:
        if isinstance(payload, str):
            return json.loads(payload)
        return payload
