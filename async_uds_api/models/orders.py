from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from async_uds_api.models.enums import (
    DeliveryTypes,
    GoodsOrderItemType,
    GoodsOrderState,
    GoodsOrderUpdateStatus,
    PaymentProvider,
    PaymentType,
)
from async_uds_api.models.goods import GoodsMeasurement
from async_uds_api.models.settings import MembershipTier

if TYPE_CHECKING:
    from async_uds_api.models.operations import PurchaseCalc


class BranchInfo(BaseModel):
    id: int = Field(description="Branch ID in the UDS.")
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
        description="Branch name.",
    )


class ParticipantShortInfo(BaseModel):
    id: int = Field(description="Customer ID in the company.")
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
        description="Customer name.",
    )


class CustomerShortInfo(ParticipantShortInfo):
    uid: str | None = Field(
        default=None,
        description="Customer UID in the UDS.",
    )
    membership_tier: MembershipTier | None = Field(
        default=None,
        alias="membershipTier",
        validation_alias="membershipTier",
    )


class ReceiverInfo(BaseModel):
    receiver_name: str | None = Field(
        default=None,
        alias="receiverName",
        validation_alias="receiverName",
        description="Name of the customer who will pick up the order.",
    )
    receiver_phone: str | None = Field(
        default=None,
        alias="receiverPhone",
        validation_alias="receiverPhone",
        description="Phone number of the customer who will pick up the order.",
    )
    user_comment: str | None = Field(
        default=None,
        alias="userComment",
        validation_alias="userComment",
        description="Customer comment on the order.",
    )


class DeliveryCase(BaseModel):
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
    type: DeliveryTypes = DeliveryTypes.PICKUP


class Delivery(ReceiverInfo):
    delivery_case: DeliveryCase | None = Field(
        default=None,
        alias="deliveryCase",
        validation_alias="deliveryCase",
    )
    address: str | None = Field(
        default=None,
        description="Delivery address.",
    )
    type: DeliveryTypes = DeliveryTypes.DELIVERY


DeliveryType = Pickup | Delivery


class OnlinePayment(BaseModel):
    payment_provider: PaymentProvider | None = Field(
        default=None,
        alias="paymentProvider",
        validation_alias="paymentProvider",
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


class PaymentMethod(BaseModel):
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
        alias="providerType",
        validation_alias="providerType",
        description="Payment provider type.",
    )


class GoodsOrderItem(BaseModel):
    id: int | None = Field(
        default=None,
        description="Item ID in the UDS.",
    )
    external_id: str | None = Field(
        default=None,
        alias="externalId",
        validation_alias="externalId",
        description="External item identifier.",
    )
    name: str = Field(description="Item name.")
    variant_name: str | None = Field(
        default=None,
        alias="variantName",
        validation_alias="variantName",
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
        alias="offerPrice",
        validation_alias="offerPrice",
        description="Discount price.",
    )
    skip_loyalty: bool = Field(
        default=False,
        alias="skipLoyalty",
        validation_alias="skipLoyalty",
        description="Don't apply loyalty program terms.",
    )
    measurement: GoodsMeasurement | None = Field(
        default=None,
        description="Goods measurement.",
    )


class GoodsOrderDetailed(BaseModel):
    id: int | None = Field(
        default=None,
        description="Order ID in the UDS.",
    )
    date_created: datetime | None = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
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
        alias="orderStatus",
        validation_alias="orderStatus",
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
        alias="certificatePoints",
        validation_alias="certificatePoints",
        description="Number of deducted certificate points.",
    )
    customer: CustomerShortInfo | None = None
    delivery: DeliveryType | None = None
    online_payment: OnlinePayment | None = Field(
        default=None,
        alias="onlinePayment",
        validation_alias="onlinePayment",
    )
    payment_method: PaymentMethod | None = Field(
        default=None,
        alias="paymentMethod",
        validation_alias="paymentMethod",
    )
    items: list[GoodsOrderItem] | None = Field(
        default=None,
        description="Items information.",
    )
    purchase: PurchaseCalc
