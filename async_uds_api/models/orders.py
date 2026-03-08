from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field

from async_uds_api.models.common import BranchInfo
from async_uds_api.models.customers import PurchaseCalc
from async_uds_api.models.goods import GoodsMeasurement
from async_uds_api.models.settings import MembershipTier


class GoodsOrderState(str, Enum):
    NEW = "NEW"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"
    WAITING_PAYMENT = "WAITING_PAYMENT"
    NEED_ACK = "NEED_ACK"


class GoodsOrderUpdateStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    READY = "READY"


class DeliveryTypes(str, Enum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


class PaymentProvider(str, Enum):
    B2P = "B2P"
    CLOUD_PAYMENTS = "CLOUD_PAYMENTS"
    YOOKASSA = "YOOKASSA"
    PAYTURE = "PAYTURE"
    CUSTOM = "CUSTOM"


class PaymentType(str, Enum):
    BEST_TO_PAY = "BEST_TO_PAY"
    CLOUD_PAYMENTS = "CLOUD_PAYMENTS"
    CASH = "CASH"
    MANUAL = "MANUAL"
    CUSTOM = "CUSTOM"


class ParticipantShortInfo(BaseModel):
    id: int = Field(description="Customer ID in the company.")
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
        description="Customer name.",
    )


class CustomerShortInfo(ParticipantShortInfo):
    uid: Optional[str] = Field(
        default=None,
        description="Customer UID in the UDS.",
    )
    membership_tier: Optional[MembershipTier] = Field(
        default=None,
        alias="membershipTier",
        validation_alias="membershipTier",
    )


class ReceiverInfo(BaseModel):
    receiver_name: Optional[str] = Field(
        default=None,
        alias="receiverName",
        validation_alias="receiverName",
        description="Name of the customer who will pick up the order.",
    )
    receiver_phone: Optional[str] = Field(
        default=None,
        alias="receiverPhone",
        validation_alias="receiverPhone",
        description="Phone number of the customer who will pick up the order.",
    )
    user_comment: Optional[str] = Field(
        default=None,
        alias="userComment",
        validation_alias="userComment",
        description="Customer comment on the order.",
    )


class DeliveryCase(BaseModel):
    name: Optional[str] = Field(
        default=None,
        description="Delivery name.",
    )
    value: Optional[float] = Field(
        default=None,
        description="Cost of delivery.",
    )


class Pickup(ReceiverInfo):
    branch: Optional[BranchInfo] = None
    type: DeliveryTypes = DeliveryTypes.PICKUP


class Delivery(ReceiverInfo):
    delivery_case: Optional[DeliveryCase] = Field(
        default=None,
        alias="deliveryCase",
        validation_alias="deliveryCase",
    )
    address: Optional[str] = Field(
        default=None,
        description="Delivery address.",
    )
    type: DeliveryTypes = DeliveryTypes.DELIVERY


DeliveryType = Union[Pickup, Delivery]


class OnlinePayment(BaseModel):
    payment_provider: Optional[PaymentProvider] = Field(
        default=None,
        alias="paymentProvider",
        validation_alias="paymentProvider",
        description="Payment provider type.",
    )
    id: Optional[str] = Field(
        default=None,
        description="Payment identifier in external payment system.",
    )
    completed: Optional[bool] = Field(
        default=None,
        description="Payment status.",
    )


class PaymentMethod(BaseModel):
    type: Optional[PaymentType] = Field(
        default=None,
        description="Payment type.",
    )
    name: Optional[str] = Field(
        default=None,
        description="Name for custom payment method with type MANUAL.",
    )
    online: Optional[bool] = Field(
        default=None,
        description="Is payment online.",
    )
    provider_type: Optional[str] = Field(
        default=None,
        alias="providerType",
        validation_alias="providerType",
        description="Payment provider type.",
    )


class GoodsOrderItem(BaseModel):
    id: Optional[int] = Field(
        default=None,
        description="Item ID in the UDS.",
    )
    external_id: Optional[str] = Field(
        default=None,
        alias="externalId",
        validation_alias="externalId",
        description="External item identifier.",
    )
    name: Optional[str] = Field(
        default=None,
        description="Item name.",
    )
    variant_name: Optional[str] = Field(
        default=None,
        alias="variantName",
        validation_alias="variantName",
        description="Name of the item option, if the type of this item is VARYING_ITEM.",
    )
    sku: Optional[str] = Field(
        default=None,
        description="Item stock number.",
    )
    type: Optional[str] = Field(
        default=None,
        description="Item type.",
    )
    qty: Optional[int] = Field(
        default=None,
        description="Quantity.",
    )
    price: Optional[float] = Field(
        default=None,
        description="Item price.",
    )
    offer_price: Optional[float] = Field(
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
    measurement: Optional[GoodsMeasurement] = Field(
        default=None,
        description="Goods measurement.",
    )


class GoodsOrderDetailed(BaseModel):
    id: Optional[int] = Field(
        default=None,
        description="Order ID in the UDS.",
    )
    date_created: Optional[datetime] = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
        description="Order date.",
    )
    comment: Optional[str] = Field(
        default=None,
        description="Comment on the order.",
    )
    state: Optional[GoodsOrderState] = Field(
        default=None,
        description="Order status.",
    )
    order_status: Optional[GoodsOrderUpdateStatus] = Field(
        default=None,
        alias="orderStatus",
        validation_alias="orderStatus",
        description="Order processing status.",
    )
    cash: Optional[float] = Field(
        default=None,
        description="Amount payable in currency units.",
    )
    points: Optional[float] = Field(
        default=None,
        description="Number of deducted points.",
    )
    total: Optional[float] = Field(
        default=None,
        description="Total order amount.",
    )
    certificate_points: Optional[float] = Field(
        default=None,
        alias="certificatePoints",
        validation_alias="certificatePoints",
        description="Number of deducted certificate points.",
    )
    customer: Optional[CustomerShortInfo] = None
    delivery: Optional[DeliveryType] = None
    online_payment: Optional[OnlinePayment] = Field(
        default=None,
        alias="onlinePayment",
        validation_alias="onlinePayment",
    )
    payment_method: Optional[PaymentMethod] = Field(
        default=None,
        alias="paymentMethod",
        validation_alias="paymentMethod",
    )
    items: Optional[List[GoodsOrderItem]] = Field(
        default=None,
        description="Items information.",
    )
    purchase: Optional[PurchaseCalc] = None
