from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from async_uds_api.models.enums import Gender, PurchaseTokenAction
from async_uds_api.models.operations import PurchaseCalcResponse
from async_uds_api.models.tags import TagModel

if TYPE_CHECKING:
    from async_uds_api.models.settings import MembershipTier


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
    gender: Gender | None = None
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


class FindCustomerResponse(PurchaseCalcResponse):
    code: str | None = Field(
        default=None,
        description=(
            "New long-term payment promo code, if exchangeCode queried."
        ),
    )
    token_type: PurchaseTokenAction | None = Field(
        default=None,
        alias="type",
        validation_alias="type",
        description="Purchase token type.",
    )
