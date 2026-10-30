"""Сценарные тесты на реальных fixtures (respx).

Проверяют ключевые сценарии и новые сигнатуры:
- reward() возвращает RewardResponse;
- calc/сreate/refund с баллами и сертификатом;
- goods_orders: update (delivery_case/items), change_status(WAITING_PAYMENT),
  complete;
- find по коду сертификата (token_type=CERTIFICATE);
- погрешность округления -> invalidChecksum.
"""

from __future__ import annotations

import json
import pathlib

import pytest
import respx
from httpx import Response

from async_uds_api import UDSBadRequestError
from async_uds_api.models import (
    CreateOperation,
    CreateOperationReceipt,
    DeliveryCase,
    GoodsOrderCompleteResult,
    GoodsOrderDetailed,
    GoodsOrderItemUpdate,
    GoodsOrderUpdateStatus,
    Operation,
    PurchaseCalcRequest,
    PurchaseCalcRequestReceipt,
    PurchaseCalcResponse,
    RewardRequest,
    RewardResponse,
)

FIXTURES = pathlib.Path(__file__).resolve().parent.parent / "fixtures"


def _load(rel: str) -> dict:
    return json.loads((FIXTURES / rel).read_text(encoding="utf-8"))


class TestRewardScenario:
    async def test_reward_returns_accepted_count(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/operations/reward").mock(
            return_value=Response(202, json={"accepted": 2})
        )

        result = await uds_client.operations.reward(
            RewardRequest(points=10, participants=[1, 2], silent=True)
        )

        assert isinstance(result, RewardResponse)
        assert result.accepted == 2


class TestPointsRedemptionScenario:
    async def test_calc_by_points_code(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/operations/calc").mock(
            return_value=Response(
                200, json=_load("api/operations/03-calc-code.json")
            )
        )

        calc = await uds_client.operations.calc(
            PurchaseCalcRequest(
                code="950692",
                receipt=PurchaseCalcRequestReceipt(total=1000.0),
            )
        )

        assert isinstance(calc, PurchaseCalcResponse)
        assert calc.purchase is not None
        assert calc.purchase.points > 0
        assert calc.purchase.cash < calc.purchase.total

    async def test_create_with_points_deducts_negative_points(
        self, uds_client
    ):
        respx.post("https://api.uds.app/partner/v2/operations").mock(
            return_value=Response(
                200, json=_load("api/operations/08-create-points-code.json")
            )
        )

        op = await uds_client.operations.create(
            CreateOperation(
                code="950692",
                receipt=CreateOperationReceipt(
                    total=1000.0, cash=750.0, points=250.0
                ),
            )
        )

        assert isinstance(op, Operation)
        assert op.points is not None and op.points < 0

    async def test_refund_is_reversal(self, uds_client):
        respx.post(
            "https://api.uds.app/partner/v2/operations/123/refund"
        ).mock(
            return_value=Response(
                200, json=_load("api/operations/14-refund-cert-code.json")
            )
        )

        op = await uds_client.operations.refund(123)

        assert isinstance(op, Operation)
        assert op.state is not None
        assert op.state.value == "REVERSAL"


class TestCertificateScenario:
    async def test_find_certificate_code(self, uds_client):
        respx.get(
            "https://api.uds.app/partner/v2/customers/find",
            params={"code": "321240"},
        ).mock(
            return_value=Response(
                200, json=_load("api/customers/01-find-cert-code.json")
            )
        )

        found = await uds_client.customers.find(code="321240")

        assert found.token_type is not None
        assert found.token_type.value == "CERTIFICATE"


class TestGoodsOrderScenario:
    async def test_update_with_delivery_case(self, uds_client):
        respx.put("https://api.uds.app/partner/v2/goods-orders/42").mock(
            return_value=Response(
                200, json=_load("api/goods_orders/11-update-need-ack.json")
            )
        )

        result = await uds_client.goods_orders.update(
            42, delivery_case=DeliveryCase(name="new zone", value=0.0)
        )

        assert isinstance(result, GoodsOrderDetailed)

    async def test_update_with_items(self, uds_client):
        respx.put("https://api.uds.app/partner/v2/goods-orders/42").mock(
            return_value=Response(
                200, json=_load("api/goods_orders/12-update-real.json")
            )
        )

        result = await uds_client.goods_orders.update(
            42,
            items=[
                GoodsOrderItemUpdate(
                    id=13901296, variant_name="Модуль", qty=2
                )
            ],
        )

        assert isinstance(result, GoodsOrderDetailed)

    async def test_change_status_to_waiting_payment(self, uds_client):
        respx.post(
            "https://api.uds.app/partner/v2/goods-orders/42/change-status"
        ).mock(
            return_value=Response(
                200,
                json=_load("api/goods_orders/14-waiting-payment-api.json"),
            )
        )

        result = await uds_client.goods_orders.change_status(
            42, GoodsOrderUpdateStatus.WAITING_PAYMENT
        )

        assert isinstance(result, GoodsOrderDetailed)
        assert result.state is not None
        assert result.state.value == "WAITING_PAYMENT"

    async def test_complete_returns_transaction(self, uds_client):
        respx.post(
            "https://api.uds.app/partner/v2/goods-orders/42/complete"
        ).mock(
            return_value=Response(
                200, json=_load("api/goods_orders/05-complete.json")
            )
        )

        result = await uds_client.goods_orders.complete(42)

        assert isinstance(result, GoodsOrderCompleteResult)
        assert result.transaction is not None
        assert isinstance(result.order, GoodsOrderDetailed)


class TestRoundingErrorScenario:
    async def test_create_with_rounding_error_rejected(self, uds_client):
        respx.post("https://api.uds.app/partner/v2/operations").mock(
            return_value=Response(
                400, json={"errorCode": "invalidChecksum", "message": "bad"}
            )
        )

        with pytest.raises(UDSBadRequestError) as exc_info:
            await uds_client.operations.create(
                CreateOperation(
                    code="966257",
                    receipt=CreateOperationReceipt(
                        total=100.05, cash=75.03999999999999, points=25.01
                    ),
                )
            )

        assert exc_info.value.error_code == "invalidChecksum"
