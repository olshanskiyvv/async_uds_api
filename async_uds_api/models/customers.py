from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from enum import Enum
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from async_uds_api.models.tags import TagModel

if TYPE_CHECKING:
    from async_uds_api.models.settings import MembershipTier


class PurchaseTokenAction(str, Enum):
    PURCHASE = "PURCHASE"
    BONUS_ITEMS_PURCHASE = "BONUS_ITEMS_PURCHASE"
    GOODS_ORDER_COMPLETE = "GOODS_ORDER_COMPLETE"
    CERTIFICATE = "CERTIFICATE"


class Participant(BaseModel):
    id: int | None = None
    inviter_id: int | None = Field(
        default=None,
        alias="inviterId",
        validation_alias="inviterId",
    )
    points: float | None = None
    discount_rate: float | None = Field(
        default=None,
        alias="discountRate",
        validation_alias="discountRate",
    )
    cashback_rate: float | None = Field(
        default=None,
        alias="cashbackRate",
        validation_alias="cashbackRate",
    )
    cash_spent: float | None = Field(
        default=None,
        alias="cashSpent",
        validation_alias="cashSpent",
    )
    saved_funds: float | None = Field(
        default=None,
        alias="savedFunds",
        validation_alias="savedFunds",
    )
    invited_count: int | None = Field(
        default=None,
        alias="invitedCount",
        validation_alias="invitedCount",
    )
    effective_invited_count: int | None = Field(
        default=None,
        alias="effectiveInvitedCount",
        validation_alias="effectiveInvitedCount",
    )
    operations_count: int | None = Field(
        default=None,
        alias="operationsCount",
        validation_alias="operationsCount",
    )
    full_refunds_count: int | None = Field(
        default=None,
        alias="fullRefundsCount",
        validation_alias="fullRefundsCount",
    )
    note: str | None = None
    membership_tier: MembershipTier | None = Field(
        default=None,
        alias="membershipTier",
        validation_alias="membershipTier",
    )
    date_created: datetime | None = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
    )
    last_transaction_time: datetime | None = Field(
        default=None,
        alias="lastTransactionTime",
        validation_alias="lastTransactionTime",
    )
    points_expire_in: datetime | None = Field(
        default=None,
        alias="pointsExpireIn",
        validation_alias="pointsExpireIn",
    )


class Customer(BaseModel):
    uid: str | None = None
    avatar: str | None = None
    display_name: str | None = Field(
        default=None,
        alias="displayName",
        validation_alias="displayName",
    )
    gender: str | None = None
    phone: str | None = None
    birth_date: date | None = Field(
        default=None,
        alias="birthDate",
        validation_alias="birthDate",
    )
    participant: Participant | None = None
    channel_name: str | None = Field(
        default=None,
        alias="channelName",
        validation_alias="channelName",
    )
    email: str | None = None


class CustomersPage(BaseModel):
    rows: list[Customer]
    cursor: str | None = None


class CustomerDetail(Customer):
    tags: Sequence[TagModel] = Field(
        default_factory=list,
        description="Customer tags list.",
    )


class PurchaseCalc(BaseModel):
    max_points: float | None = Field(
        default=None,
        alias="maxPoints",
        validation_alias="maxPoints",
        description="Maximum number of points available.",
    )
    total: float | None = Field(
        default=None,
        description="Total bill (in currency units).",
    )
    skip_loyalty_total: float | None = Field(
        default=None,
        alias="skipLoyaltyTotal",
        validation_alias="skipLoyaltyTotal",
        description="Part of bill amount without cashback/discount.",
    )
    unredeemable_total: float | None = Field(
        default=None,
        alias="unredeemableTotal",
        validation_alias="unredeemableTotal",
        description="Part of total that cannot be redeemed with points.",
    )
    discount_amount: float | None = Field(
        default=None,
        alias="discountAmount",
        validation_alias="discountAmount",
        description="Discount amount (in currency units).",
    )
    discount_percent: float | None = Field(
        default=None,
        alias="discountPercent",
        validation_alias="discountPercent",
        description="Discount rate (as a percentage).",
    )
    points: float | None = Field(
        default=None,
        description="Payable points.",
    )
    points_percent: float | None = Field(
        default=None,
        alias="pointsPercent",
        validation_alias="pointsPercent",
        description="Discount rate due to points (as a percentage).",
    )
    net_discount: float | None = Field(
        default=None,
        alias="netDiscount",
        validation_alias="netDiscount",
        description="Total discount amount (in currency units).",
    )
    net_discount_percent: float | None = Field(
        default=None,
        alias="netDiscountPercent",
        validation_alias="netDiscountPercent",
        description="Total discount rate (as a percentage of the total bill).",
    )
    certificate_points: float | None = Field(
        default=None,
        alias="certificatePoints",
        validation_alias="certificatePoints",
        description="Number of deducted certificate points.",
    )
    cash: float | None = Field(
        default=None,
        description="Payable amount (in currency units).",
    )
    cash_total: float | None = Field(
        default=None,
        alias="cashTotal",
        validation_alias="cashTotal",
        description="Total amount to be paid including extras.",
    )
    cashback: float | None = Field(
        default=None,
        alias="cashBack",
        validation_alias="cashBack",
        description=(
            "Reward (cashback) to be accrued after transaction completion "
            "(in points)."
        ),
    )
    extras_delivery: float | None = Field(
        default=None,
        alias="extras",
        validation_alias="extras",
        description="Delivery cost (in currency units).",
    )
    max_scores_discount: float | None = Field(
        default=None,
        alias="maxScoresDiscount",
        validation_alias="maxScoresDiscount",
        description=(
            "Maximum discount (as a percentage) allowed for redeeming points."
        ),
    )


class PurchaseCalcRequestParticipant(BaseModel):
    uid: str | None = None
    phone: str | None = None


class PurchaseCalcRequestReceipt(BaseModel):
    total: float
    skip_loyalty_total: float | None = Field(
        default=None,
        alias="skipLoyaltyTotal",
        validation_alias="skipLoyaltyTotal",
    )
    unredeemable_total: float | None = Field(
        default=None,
        alias="unredeemableTotal",
        validation_alias="unredeemableTotal",
    )
    points: float | None = None


class PurchaseCalcRequest(BaseModel):
    code: str | None = None
    participant: PurchaseCalcRequestParticipant | None = None
    receipt: PurchaseCalcRequestReceipt


class PurchaseCalcResponse(BaseModel):
    user: CustomerDetail
    purchase: PurchaseCalc | None = None
    code: str | None = None
    type: PurchaseTokenAction | None = None


class OperationCustomerShortInfo(BaseModel):
    id: int
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
    )


class OperationCustomer(OperationCustomerShortInfo):
    uid: str | None = None
