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
        description=(
            "Upgrade status when customer reaches that amount of cash spent."
        ),
    )
    effective_invited_count: (
        MembershipTierConditionsEffectiveInvitedCount | None
    ) = Field(
        default=None,
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
        description=(
            "Maximum discount (as a percentage) allowed for redeeming points."
        ),
    )
    conditions: MembershipTierConditions | None = Field(
        default=None,
        description="Conditions to upgrade customer's status automatically.",
    )


class LoyaltyProgramSettings(APIModel):
    base_membership_tier: MembershipTier
    membership_tiers: list[MembershipTier] = Field(
        description="Status settings.",
    )
    referral_cashback_rates: list[float] = Field(
        description="Referral cashback rates (3 levels as a percentage).",
    )
    cashier_award: float | None = Field(
        default=None,
        description="Cashier's reward rate for the performed transaction.",
    )
    referral_reward: float | None = Field(
        default=None,
        description="Customer's reward for an effective recommendation.",
    )
    discount_vip: float | None = Field(
        default=None,
        description="VIP discount rate.",
    )
    receipt_limit: float | None = Field(
        default=None,
        description=(
            "Maximum transaction amount that can be made through UDS Cashier."
        ),
    )
    defer_points_for_days: float | None = Field(
        default=None,
        description="Term (in days) to accrue deferred points.",
    )
    first_purchase_points: float | None = Field(
        default=None,
        description="Number of points for the first purchase.",
        ge=0.01,
    )


class CompanySettings(APIModel):
    id: int = Field(description="Company ID.")
    name: str = Field(description="Company name.")
    promo_code: str = Field(
        description="Company promo code for customers to join.",
    )
    currency: str | None = Field(
        default=None,
        description="Currency in ISO-4217 format.",
    )
    base_discount_policy: BaseDiscountPolicy = Field(
        description="Defines loyalty program type.",
    )
    loyalty_program_settings: LoyaltyProgramSettings | None = None
    purchase_by_phone: bool = Field(
        description="Permission to make purchases by phone number.",
    )
    use_points_by_phone: bool = Field(
        description="Permission to spend points purchases by phone number.",
    )
    write_invoice: bool = Field(
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
