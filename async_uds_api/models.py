from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional, Sequence

from pydantic import BaseModel, Field


class MembershipTierConditionsTotalCashSpent(BaseModel):
    target: float = Field(description="Amount of cash spent.")


class MembershipTierConditionsEffectiveInvitedCount(BaseModel):
    target: int = Field(description="Amount of invited count.")


class MembershipTierConditions(BaseModel):
    total_cash_spent: Optional[MembershipTierConditionsTotalCashSpent] = Field(
        default=None,
        description="Upgrade status when customer reaches that amount of cash spent.",
    )
    effective_invited_count: Optional[MembershipTierConditionsEffectiveInvitedCount] = Field(
        default=None,
        description="Upgrade to tier when customer reaches target effectiveInvitedCount.",
    )


class MembershipTier(BaseModel):
    uid: Optional[str] = Field(
        default=None,
        description="Status UID.",
    )
    name: str = Field(description="Status name.")
    rate: float = Field(description="Status rate.")
    max_scores_discount: Optional[float] = Field(
        default=None,
        description="Maximum discount (as a percentage) allowed for redeeming points.",
    )
    conditions: Optional[MembershipTierConditions] = Field(
        default=None,
        description="Conditions to upgrade customer's status automatically.",
    )


class LoyaltyProgramSettings(BaseModel):
    base_membership_tier: MembershipTier = Field(
        alias="baseMembershipTier",
        validation_alias="baseMembershipTier",
    )
    membership_tiers: List[MembershipTier] = Field(
        alias="membershipTiers",
        validation_alias="membershipTiers",
        description="Status settings.",
    )
    referral_cashback_rates: List[float] = Field(
        alias="referralCashbackRates",
        validation_alias="referralCashbackRates",
        description="Referral cashback rates (3 levels as a percentage).",
    )
    cashier_award: Optional[float] = Field(
        default=None,
        alias="cashierAward",
        validation_alias="cashierAward",
        description="Cashier’s reward rate for the performed transaction.",
    )
    referral_reward: Optional[float] = Field(
        default=None,
        alias="referralReward",
        validation_alias="referralReward",
        description="Customer’s reward for an effective recommendation.",
    )
    receipt_limit: Optional[float] = Field(
        default=None,
        alias="receiptLimit",
        validation_alias="receiptLimit",
        description="Maximum transaction amount that can be made through UDS Cashier.",
    )
    defer_points_for_days: Optional[float] = Field(
        default=None,
        alias="deferPointsForDays",
        validation_alias="deferPointsForDays",
        description="Term (in days) to accrue deferred points.",
    )
    first_purchase_points: Optional[float] = Field(
        default=None,
        alias="firstPurchasePoints",
        validation_alias="firstPurchasePoints",
        description="Number of points for the first purchase.",
    )


class CompanySettings(BaseModel):
    id: int = Field(description="Company ID.")
    name: str = Field(description="Company name.")
    promo_code: str = Field(
        alias="promoCode",
        validation_alias="promoCode",
        description="Company promo code for customers to join.",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency in ISO-4217 format.",
    )
    base_discount_policy: str = Field(
        alias="baseDiscountPolicy",
        validation_alias="baseDiscountPolicy",
        description="Defines loyalty program type.",
    )
    loyalty_program_settings: Optional[LoyaltyProgramSettings] = Field(
        default=None,
        alias="loyaltyProgramSettings",
        validation_alias="loyaltyProgramSettings",
    )
    purchase_by_phone: bool = Field(
        alias="purchaseByPhone",
        validation_alias="purchaseByPhone",
        description="Permission to make purchases by phone number.",
    )
    use_points_by_phone: bool = Field(
        alias="usePointsByPhone",
        validation_alias="usePointsByPhone",
        description="Permission to spend points purchases by phone number.",
    )
    write_invoice: bool = Field(
        alias="writeInvoice",
        validation_alias="writeInvoice",
        description="Necessity to indicate a bill number when performing transactions through UDS Cashier.",
    )
    slug: str = Field(
        description="The domain name that appears in the link to your company's web page.",
    )


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


class TagModel(BaseModel):
    id: int = Field(description="Tag identifier.")
    name: str = Field(description="Tag name.")


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


class CashierInfo(BaseModel):
    id: int
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
    )


class BranchInfo(BaseModel):
    id: int
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
    )


class Operation(BaseModel):
    id: Optional[int] = Field(default=None, description="Transaction ID in the UDS.")
    date_created: Optional[datetime] = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
        description="Transaction date.",
    )
    action: Optional[str] = None
    state: Optional[str] = None
    customer: Optional[OperationCustomer] = None
    cashier: Optional[CashierInfo] = None
    branch: Optional[BranchInfo] = None
    points: Optional[float] = None
    certificate_points: Optional[float] = Field(
        default=None,
        alias="certificatePoints",
        validation_alias="certificatePoints",
    )
    receipt_number: Optional[str] = Field(
        default=None,
        alias="receiptNumber",
        validation_alias="receiptNumber",
    )


class OperationsPage(BaseModel):
    rows: List[Operation]
    total: Optional[int] = None
    cursor: Optional[str] = None


class CreateOperationParticipant(BaseModel):
    uid: Optional[str] = None
    phone: Optional[str] = None


class CreateOperationReceipt(BaseModel):
    total: float
    cash: float
    points: float
    number: Optional[str] = None
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


class CreateOperation(BaseModel):
    code: Optional[str] = None
    participant: Optional[CreateOperationParticipant] = None
    nonce: Optional[str] = None
    cashier_external_id: Optional[str] = Field(
        default=None,
        alias="cashierExternalId",
        description="External cashier identifier.",
    )
    cashier_name: Optional[str] = Field(
        default=None,
        alias="cashierName",
        description="Cashier name.",
    )
    receipt: CreateOperationReceipt
    tags: Optional[List[int]] = None


class RefundOperationRequest(BaseModel):
    partial_amount: Optional[float] = Field(
        default=None,
        alias="partialAmount",
        validation_alias="partialAmount",
        description="Refund amount.",
    )


class RewardRequest(BaseModel):
    comment: Optional[str] = None
    points: float
    participants: List[int]
    silent: bool = False


