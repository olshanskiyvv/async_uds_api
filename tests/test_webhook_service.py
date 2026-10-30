"""Тесты сервиса `client.webhooks` (проверка подписи и поименные парсеры)."""

from __future__ import annotations

import hashlib
import json
import pathlib
import re

from async_uds_api.models import Customer, GoodsOrderDetailed, Operation

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures" / "webhooks"


def _load(rel: str) -> dict:
    return json.loads((FIXTURES / rel).read_text(encoding="utf-8"))


def _to_snake(value: object) -> object:
    """Рекурсивно перевести ключи dict из camelCase в snake_case."""
    if isinstance(value, dict):
        return {
            re.sub(r"(?<!^)(?=[A-Z])", "_", key).lower(): _to_snake(v)
            for key, v in value.items()
        }
    if isinstance(value, list):
        return [_to_snake(item) for item in value]
    return value


class TestVerifySignature:
    def test_verify_signature_valid(self, uds_client):
        request_id = "bf7d19b0-8e3c-4d55-98ba-2783915957b3"
        timestamp = "2018-10-22T13:52:46,769Z"
        concatenated = f"{request_id}{timestamp}123456test-api-key"
        signature = hashlib.md5(concatenated.encode()).hexdigest()

        result = uds_client.webhooks.verify_signature(
            request_id, timestamp, signature
        )

        assert result is True

    def test_verify_signature_invalid(self, uds_client):
        result = uds_client.webhooks.verify_signature(
            "test-id", "2024-01-01T00:00:00Z", "invalid"
        )

        assert result is False


class TestWebhookParsers:
    def test_parse_goods_order_from_dict(self, uds_client):
        order = uds_client.webhooks.parse_goods_order(
            _load("goods-order/01-cert.json")
        )

        assert isinstance(order, GoodsOrderDetailed)

    def test_parse_goods_order_from_str(self, uds_client):
        raw = (FIXTURES / "goods-order/01-cert.json").read_text(
            encoding="utf-8"
        )

        order = uds_client.webhooks.parse_goods_order(raw)

        assert isinstance(order, GoodsOrderDetailed)

    def test_parse_goods_order_from_snake_case_dict(self, uds_client):
        data = _to_snake(_load("goods-order/01-cert.json"))

        order = uds_client.webhooks.parse_goods_order(data)

        assert isinstance(order, GoodsOrderDetailed)

    def test_parse_operation(self, uds_client):
        op = uds_client.webhooks.parse_operation(
            _load("operation/01-canceled.json")
        )

        assert isinstance(op, Operation)

    def test_parse_participant(self, uds_client):
        customer = uds_client.webhooks.parse_participant(
            _load("participant.json")
        )

        assert isinstance(customer, Customer)
