from __future__ import annotations

from collections.abc import Sequence
from datetime import date, datetime

from pydantic import Field

from async_uds_api.models.base import APIModel
from async_uds_api.models.enums import Gender, PurchaseTokenAction
from async_uds_api.models.operations import PurchaseCalc
from async_uds_api.models.settings import MembershipTier
from async_uds_api.models.tags import TagModel


class Participant(APIModel):
    id: int | None = None
    inviter_id: int | None = None
    points: float | None = None
    discount_rate: float | None = None
    cashback_rate: float | None = None
    cash_spent: float | None = None
    saved_funds: float | None = None
    invited_count: int | None = None
    effective_invited_count: int | None = None
    operations_count: int | None = None
    full_refunds_count: int | None = None
    note: str | None = None
    membership_tier: MembershipTier | None = None
    date_created: datetime | None = None
    last_transaction_time: datetime | None = None
    points_expire_in: datetime | None = None


class Customer(APIModel):
    uid: str | None = None
    avatar: str | None = None
    display_name: str | None = None
    gender: Gender | None = None
    phone: str | None = None
    birth_date: date | None = None
    participant: Participant | None = None
    channel_name: str | None = None
    email: str | None = None


class CustomersPage(APIModel):
    rows: list[Customer]
    cursor: str | None = None


class CustomerDetail(Customer):
    tags: Sequence[TagModel] = Field(
        default_factory=list,
        description="Customer tags list.",
    )


class PurchaseCalcResponse(APIModel):
    user: CustomerDetail
    purchase: PurchaseCalc | None = None


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
