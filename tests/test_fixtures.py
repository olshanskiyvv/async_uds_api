"""Проверка, что все реальные fixtures парсятся моделями без потерь.

Покрывает:
- разбор всех 63 fixture (api/ и webhooks/);
- новые поля схемы, которые раньше «тихо терялись»: membership_tier у операции,
  system у уровня, external_order и физические параметры у заказа.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from async_uds_api.models import (
    CompanySettings,
    Customer,
    CustomerDetail,
    CustomersPage,
    FindCustomerResponse,
    GoodsDetailed,
    GoodsOrderCode,
    GoodsOrderCompleteResult,
    GoodsOrderDetailed,
    GoodsPage,
    ImageUploadUrl,
    Operation,
    OperationsPage,
    PurchaseCalcResponse,
    TagsPage,
    VoucherInfo,
)

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def _strip_num(name: str) -> str:
    """'01-calc.json' -> 'calc.json'."""
    head, sep, tail = name.partition("-")
    return tail if sep and head.isdigit() else name


def _model_for(rel: pathlib.Path) -> type:
    rel_str = rel.as_posix()
    if rel_str.startswith("webhooks/"):
        if rel_str == "webhooks/participant.json":
            return Customer
        if rel_str.startswith("webhooks/goods-order/"):
            return GoodsOrderDetailed
        if rel_str.startswith("webhooks/operation/"):
            return Operation
        raise ValueError(f"unknown webhook fixture: {rel_str}")

    # api/
    if rel_str == "api/settings.json":
        return CompanySettings
    if rel_str == "api/tags.json":
        return TagsPage
    if rel_str == "api/images.json":
        return ImageUploadUrl
    if rel_str.startswith("api/customers/"):
        name = _strip_num(rel_str.split("/")[-1])
        if name.startswith("find-"):
            return FindCustomerResponse
        if name.startswith("get-tags") or name.startswith("set-tags"):
            return TagsPage
        if name.startswith("get"):
            return CustomerDetail
        return CustomersPage
    if rel_str.startswith("api/operations/"):
        name = _strip_num(rel_str.split("/")[-1])
        if name.startswith("calc"):
            return PurchaseCalcResponse
        if "voucher" in name:
            return VoucherInfo
        if name.startswith("list"):
            return OperationsPage
        return Operation
    if rel_str.startswith("api/goods/"):
        if rel_str.endswith("list.json"):
            return GoodsPage
        return GoodsDetailed
    if rel_str.startswith("api/goods_orders/"):
        name = rel_str.split("/")[-1]
        if "complete" in name:
            return GoodsOrderCompleteResult
        if "generate-code" in name:
            return GoodsOrderCode
        return GoodsOrderDetailed
    raise ValueError(f"unknown api fixture: {rel_str}")


def _all_fixtures() -> list[tuple[str, type]]:
    result: list[tuple[str, type]] = []
    for p in sorted((FIXTURES / "api").rglob("*.json")):
        rel = p.relative_to(FIXTURES)
        result.append((rel.as_posix(), _model_for(rel)))
    for p in sorted((FIXTURES / "webhooks").rglob("*.json")):
        rel = p.relative_to(FIXTURES)
        result.append((rel.as_posix(), _model_for(rel)))
    return result


_ALL = _all_fixtures()


@pytest.mark.parametrize(
    "rel, model", _ALL, ids=[rel for rel, _ in _ALL]
)
def test_fixture_parses(rel: str, model: type) -> None:
    data = json.loads((FIXTURES / rel).read_text(encoding="utf-8"))
    obj = model.model_validate(data)
    assert obj is not None


def _load(rel: str) -> dict:
    return json.loads((FIXTURES / rel).read_text(encoding="utf-8"))


def test_operation_customer_has_membership_tier() -> None:
    op = Operation.model_validate(_load("webhooks/operation/01-canceled.json"))
    assert op.customer is not None
    assert op.customer.membership_tier is not None
    assert op.customer.membership_tier.system is False


def test_goods_order_has_external_order_and_physical_fields() -> None:
    order = GoodsOrderDetailed.model_validate(
        _load("webhooks/goods-order/01-cert.json")
    )
    assert order.external_order is None
    assert order.customer is not None
    assert order.customer.membership_tier is not None
    assert order.customer.membership_tier.system is False
    assert order.items is not None
    item = order.items[0]
    assert item.data_matrix_codes is None
    assert item.delivery_state is None
    assert item.weight_grams is None
    assert item.width_cm is None
    assert item.height_cm is None
    assert item.length_cm is None


def test_participant_webhook_is_customer() -> None:
    customer = Customer.model_validate(_load("webhooks/participant.json"))
    assert customer.uid is not None
    assert customer.participant is not None
    assert customer.participant.membership_tier is not None
