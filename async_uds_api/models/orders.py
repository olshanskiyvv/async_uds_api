from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from async_uds_api.models.base import APIModel
from async_uds_api.models.common import BranchInfo, ParticipantShortInfo
from async_uds_api.models.enums import (
    DeliveryTypes,
    GoodsMeasurement,
    GoodsOrderItemType,
    GoodsOrderState,
    GoodsOrderUpdateStatus,
    PaymentProvider,
    PaymentType,
)
from async_uds_api.models.operations import PurchaseCalc
from async_uds_api.models.settings import MembershipTier


class CustomerShortInfo(ParticipantShortInfo):
    uid: str | None = Field(
        default=None,
        description="Customer UID in the UDS.",
    )
    membership_tier: MembershipTier | None = None


class ReceiverInfo(APIModel):
    receiver_name: str | None = Field(
        default=None,
        description="Name of the customer who will pick up the order.",
    )
    receiver_phone: str | None = Field(
        default=None,
        description="Phone number of the customer who will pick up the order.",
    )
    user_comment: str | None = Field(
        default=None,
        description="Customer comment on the order.",
    )


class DeliveryCase(APIModel):
    name: str | None = Field(
        default=None,
        description="Delivery name.",
    )
    value: float | None = Field(
        default=None,
        description="Cost of delivery.",
    )


class Pickup(ReceiverInfo):
    branch: BranchInfo | None = None
    type: Literal[DeliveryTypes.PICKUP] = DeliveryTypes.PICKUP


class Delivery(ReceiverInfo):
    delivery_case: DeliveryCase | None = None
    address: str | None = Field(
        default=None,
        description="Delivery address.",
    )
    type: Literal[DeliveryTypes.DELIVERY] = DeliveryTypes.DELIVERY


DeliveryType = Annotated[Pickup | Delivery, Field(discriminator="type")]


class OnlinePayment(APIModel):
    payment_provider: PaymentProvider | None = Field(
        default=None,
        description="Payment provider type.",
    )
    id: str | None = Field(
        default=None,
        description="Payment identifier in external payment system.",
    )
    completed: bool | None = Field(
        default=None,
        description="Payment status.",
    )


class PaymentMethod(APIModel):
    type: PaymentType | None = Field(
        default=None,
        description="Payment type.",
    )
    name: str | None = Field(
        default=None,
        description="Name for custom payment method with type MANUAL.",
    )
    online: bool | None = Field(
        default=None,
        description="Is payment online.",
    )
    provider_type: str | None = Field(
        default=None,
        description="Payment provider type.",
    )


class GoodsOrderItem(APIModel):
    id: int | None = Field(
        default=None,
        description="Item ID in the UDS.",
    )
    external_id: str | None = Field(
        default=None,
        description="External item identifier.",
    )
    name: str = Field(description="Item name.")
    variant_name: str | None = Field(
        default=None,
        description=(
            "Name of the item option, if the type of this item is "
            "VARYING_ITEM."
        ),
    )
    sku: str | None = Field(
        default=None,
        description="Item stock number.",
    )
    type: GoodsOrderItemType = Field(description="Item type.")
    qty: int = Field(description="Quantity.")
    price: float = Field(description="Item price.")
    offer_price: float | None = Field(
        default=None,
        description="Discount price.",
    )
    skip_loyalty: bool = Field(
        default=False,
        description="Don't apply loyalty program terms.",
    )
    measurement: GoodsMeasurement | None = Field(
        default=None,
        description="Goods measurement.",
    )


class GoodsOrderItemUpdate(APIModel):
    id: int | None = Field(default=None, description="Item ID in the UDS.")
    variant_name: str | None = Field(
        default=None,
        description=(
            "Name of the item option, if the type of this item is "
            "VARYING_ITEM."
        ),
    )
    qty: int | None = Field(default=None, description="Quantity.")


class GoodsOrderItemNew(APIModel):
    external_id: str | None = Field(
        default=None,
        description="External item identifier.",
    )
    name: str | None = Field(default=None, description="Item name.")
    variant_name: str | None = Field(
        default=None,
        description=(
            "Name of the item option, if the type of this item is "
            "VARYING_ITEM."
        ),
    )
    qty: int | None = Field(default=None, description="Quantity.")
    price: float | None = Field(default=None, description="Item price.")
    skip_loyalty: bool = Field(
        default=False,
        description="Don't apply loyalty program terms.",
    )


class GoodsOrderUpdate(APIModel):
    delivery_case: DeliveryCase | None = None
    items: list[GoodsOrderItemUpdate | GoodsOrderItemNew] | None = Field(
        default=None,
        description="Items information.",
    )


class GoodsOrderDetailed(APIModel):
    id: int | None = Field(
        default=None,
        description="Order ID in the UDS.",
    )
    date_created: datetime | None = Field(
        default=None,
        description="Order date.",
    )
    comment: str | None = Field(
        default=None,
        description="Comment on the order.",
    )
    state: GoodsOrderState | None = Field(
        default=None,
        description="Order status.",
    )
    order_status: GoodsOrderUpdateStatus | None = Field(
        default=None,
        description="Order processing status.",
    )
    cash: float | None = Field(
        default=None,
        description="Amount payable in currency units.",
    )
    points: float | None = Field(
        default=None,
        description="Number of deducted points.",
    )
    total: float | None = Field(
        default=None,
        description="Total order amount.",
    )
    certificate_points: float | None = Field(
        default=None,
        description="Number of deducted certificate points.",
    )
    customer: CustomerShortInfo | None = None
    delivery: DeliveryType | None = None
    online_payment: OnlinePayment | None = None
    payment_method: PaymentMethod | None = None
    items: list[GoodsOrderItem] | None = Field(
        default=None,
        description="Items information.",
    )
    purchase: PurchaseCalc


class GoodsOrderCode(APIModel):
    code: str = Field(description="Payment code to complete the order.")
