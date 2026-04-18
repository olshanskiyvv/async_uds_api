from __future__ import annotations

from pydantic import Field

from async_uds_api.models.base import APIModel
from async_uds_api.models.enums import BaseDiscountPolicy


class MembershipTierConditionsTotalCashSpent(APIModel):
    target: float | None = Field(
        default=None, description="Amount of cash spent."
    )


class MembershipTierConditionsEffectiveInvitedCount(APIModel):
    target: int | None = Field(
        default=None, description="Amount of invited count."
    )


class MembershipTierConditions(APIModel):
    total_cash_spent: MembershipTierConditionsTotalCashSpent | None = Field(
        default=None,
        alias="totalCashSpent",
        validation_alias="totalCashSpent",
        description=(
            "Upgrade status when customer reaches that amount of cash spent."
        ),
    )
    effective_invited_count: (
        MembershipTierConditionsEffectiveInvitedCount | None
    ) = Field(
        default=None,
        alias="effectiveInvitedCount",
        validation_alias="effectiveInvitedCount",
        description=(
            "Upgrade to tier when customer reaches target "
            "effectiveInvitedCount."
        ),
    )


class MembershipTier(APIModel):
    uid: str | None = Field(
        default=None,
        description="Status UID.",
    )
    name: str = Field(description="Status name.")
    rate: float = Field(description="Status rate.", ge=0, le=100)
    max_scores_discount: float | None = Field(
        default=None,
        alias="maxScoresDiscount",
        validation_alias="maxScoresDiscount",
        description=(
            "Maximum discount (as a percentage) allowed for redeeming points."
        ),
    )
    conditions: MembershipTierConditions | None = Field(
        default=None,
        description="Conditions to upgrade customer's status automatically.",
    )


class LoyaltyProgramSettings(APIModel):
    base_membership_tier: MembershipTier = Field(
        alias="baseMembershipTier",
        validation_alias="baseMembershipTier",
    )
    membership_tiers: list[MembershipTier] = Field(
        alias="membershipTiers",
        validation_alias="membershipTiers",
        description="Status settings.",
    )
    referral_cashback_rates: list[float] = Field(
        alias="referralCashbackRates",
        validation_alias="referralCashbackRates",
        description="Referral cashback rates (3 levels as a percentage).",
    )
    cashier_award: float | None = Field(
        default=None,
        alias="cashierAward",
        validation_alias="cashierAward",
        description="Cashier's reward rate for the performed transaction.",
    )
    referral_reward: float | None = Field(
        default=None,
        alias="referralReward",
        validation_alias="referralReward",
        description="Customer's reward for an effective recommendation.",
    )
    discount_vip: float | None = Field(
        default=None,
        alias="discountVip",
        validation_alias="discountVip",
        description="VIP discount rate.",
    )
    receipt_limit: float | None = Field(
        default=None,
        alias="receiptLimit",
        validation_alias="receiptLimit",
        description=(
            "Maximum transaction amount that can be made through UDS Cashier."
        ),
    )
    defer_points_for_days: float | None = Field(
        default=None,
        alias="deferPointsForDays",
        validation_alias="deferPointsForDays",
        description="Term (in days) to accrue deferred points.",
    )
    first_purchase_points: float | None = Field(
        default=None,
        alias="firstPurchasePoints",
        validation_alias="firstPurchasePoints",
        description="Number of points for the first purchase.",
        ge=0.01,
    )


class CompanySettings(APIModel):
    id: int = Field(description="Company ID.")
    name: str = Field(description="Company name.")
    promo_code: str = Field(
        alias="promoCode",
        validation_alias="promoCode",
        description="Company promo code for customers to join.",
    )
    currency: str | None = Field(
        default=None,
        description="Currency in ISO-4217 format.",
    )
    base_discount_policy: BaseDiscountPolicy = Field(
        alias="baseDiscountPolicy",
        validation_alias="baseDiscountPolicy",
        description="Defines loyalty program type.",
    )
    loyalty_program_settings: LoyaltyProgramSettings | None = Field(
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
        description=(
            "Necessity to indicate a bill number when performing "
            "transactions through UDS Cashier."
        ),
    )
    slug: str = Field(
        description=(
            "The domain name that appears in the link to your company's "
            "web page."
        ),
    )
