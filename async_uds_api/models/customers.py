from __future__ import annotations

from datetime import date
from typing import List, Optional, Sequence

from pydantic import BaseModel, Field

from async_uds_api.models.tags import TagModel


class Participant(BaseModel):
    uid: Optional[str] = None
    code: Optional[str] = None
    membership_tier_name: Optional[str] = Field(
        default=None,
        alias="membershipTierName",
        validation_alias="membershipTierName",
    )
    scores: Optional[float] = None
    cash: Optional[float] = None


class Customer(BaseModel):
    uid: Optional[str] = None
    avatar: Optional[str] = None
    display_name: Optional[str] = Field(
        default=None,
        alias="displayName",
        validation_alias="displayName",
    )
    gender: Optional[str] = None
    phone: Optional[str] = None
    birth_date: Optional[date] = Field(
        default=None,
        alias="birthDate",
        validation_alias="birthDate",
    )
    participant: Optional[Participant] = None
    channel_name: Optional[str] = Field(
        default=None,
        alias="channelName",
        validation_alias="channelName",
    )
    email: Optional[str] = None


class CustomersPage(BaseModel):
    rows: List[Customer]


class CustomerDetail(Customer):
    tags: Sequence[TagModel] = Field(
        default_factory=list,
        description="Customer tags list.",
    )


class PurchaseCalc(BaseModel):
    max_points: Optional[float] = Field(
        default=None,
        alias="maxPoints",
        validation_alias="maxPoints",
        description="Maximum number of points available.",
    )
    total: Optional[float] = Field(
        default=None,
        description="Total bill (in currency units).",
    )
    skip_loyalty_total: Optional[float] = Field(
        default=None,
        alias="skipLoyaltyTotal",
        validation_alias="skipLoyaltyTotal",
        description="Part of bill amount without cashback/discount.",
    )
    unredeemable_total: Optional[float] = Field(
        default=None,
        alias="unredeemableTotal",
        validation_alias="unredeemableTotal",
        description="Part of total that cannot be redeemed with points.",
    )
    discount_amount: Optional[float] = Field(
        default=None,
        alias="discountAmount",
        validation_alias="discountAmount",
        description="Discount amount (in currency units).",
    )
    discount_percent: Optional[float] = Field(
        default=None,
        alias="discountPercent",
        validation_alias="discountPercent",
        description="Discount rate (as a percentage).",
    )
    points: Optional[float] = Field(
        default=None,
        description="Payable points.",
    )
    points_percent: Optional[float] = Field(
        default=None,
        alias="pointsPercent",
        validation_alias="pointsPercent",
        description="Discount rate due to points (as a percentage).",
    )
    net_discount: Optional[float] = Field(
        default=None,
        alias="netDiscount",
        validation_alias="netDiscount",
        description="Total discount amount (in currency units).",
    )
    net_discount_percent: Optional[float] = Field(
        default=None,
        alias="netDiscountPercent",
        validation_alias="netDiscountPercent",
        description="Total discount rate (as a percentage of the total bill).",
    )
    certificate_points: Optional[float] = Field(
        default=None,
        alias="certificatePoints",
        validation_alias="certificatePoints",
        description="Number of deducted certificate points.",
    )
    cash: Optional[float] = Field(
        default=None,
        description="Payable amount (in currency units).",
    )
    cash_total: Optional[float] = Field(
        default=None,
        alias="cashTotal",
        validation_alias="cashTotal",
        description="Total amount to be paid including extras.",
    )
    cashback: Optional[float] = Field(
        default=None,
        alias="cashBack",
        validation_alias="cashBack",
        description="Reward (cashback) to be accrued after transaction completion (in points).",
    )
    extras_delivery: Optional[float] = Field(
        default=None,
        alias="extras",
        validation_alias="extras",
        description="Delivery cost (in currency units).",
    )
    max_scores_discount: Optional[float] = Field(
        default=None,
        alias="maxScoresDiscount",
        validation_alias="maxScoresDiscount",
        description="Maximum discount (as a percentage) allowed for redeeming points.",
    )


class PurchaseCalcRequestParticipant(BaseModel):
    uid: Optional[str] = None
    phone: Optional[str] = None


class PurchaseCalcRequestReceipt(BaseModel):
    total: float
    skip_loyalty_total: Optional[float] = Field(
        default=None,
        alias="skipLoyaltyTotal",
        validation_alias="skipLoyaltyTotal",
    )
    unredeemable_total: Optional[float] = Field(
        default=None,
        alias="unredeemableTotal",
        validation_alias="unredeemableTotal",
    )
    points: Optional[float] = None


class PurchaseCalcRequest(BaseModel):
    code: Optional[str] = None
    participant: Optional[PurchaseCalcRequestParticipant] = None
    receipt: PurchaseCalcRequestReceipt


class PurchaseCalcResponse(BaseModel):
    user: CustomerDetail
    purchase: PurchaseCalc


class OperationCustomerShortInfo(BaseModel):
    id: int
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
    )


class OperationCustomer(OperationCustomerShortInfo):
    uid: Optional[str] = None
