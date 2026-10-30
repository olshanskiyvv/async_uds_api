from __future__ import annotations

from datetime import datetime

from pydantic import Field

from async_uds_api.models.base import APIModel
from async_uds_api.models.common import BranchInfo, ParticipantShortInfo
from async_uds_api.models.enums import Action, ActionState
from async_uds_api.models.settings import MembershipTier


class OperationCustomer(ParticipantShortInfo):
    """Customer from an operation."""

    uid: str | None = None
    membership_tier: MembershipTier | None = Field(
        default=None,
        description="Customer membership tier (present in real payloads).",
    )


class CashierInfo(APIModel):
    """Cashier information."""

    id: int
    display_name: str


class OperationOrigin(APIModel):
    """Operation origin."""

    id: int | None = None


class Operation(APIModel):
    """Operation (purchase, refund, reward, etc.)."""

    id: int | None = Field(
        default=None, description="Transaction ID in the UDS."
    )
    date_created: datetime | None = Field(
        default=None,
        description="Transaction date.",
    )
    action: Action
    state: ActionState | None = None
    customer: OperationCustomer | None = None
    cashier: CashierInfo | None = None
    branch: BranchInfo | None = None
    points: float | None = None
    certificate_points: float | None = None
    receipt_number: str | None = None
    origin: OperationOrigin | None = None
    total: float | None = None
    cash: float | None = None


class OperationsPage(APIModel):
    """A page of operations."""

    rows: list[Operation]
    total: int | None = None
    cursor: str | None = None


class CreateOperationParticipant(APIModel):
    """Participant for creating an operation."""

    uid: str | None = None
    phone: str | None = None


class CashierInput(APIModel):
    """Cashier for creating an operation."""

    external_id: str
    name: str | None = None


class CreateOperationReceipt(APIModel):
    """Receipt for creating an operation."""

    total: float
    cash: float
    points: float
    number: str | None = None
    skip_loyalty_total: float | None = None
    unredeemable_total: float | None = None


class CreateOperation(APIModel):
    """Request to create an operation."""

    code: str | None = None
    participant: CreateOperationParticipant | None = None
    nonce: str | None = None
    cashier: CashierInput | None = None
    receipt: CreateOperationReceipt
    tags: list[int] | None = None


class RefundOperationRequest(APIModel):
    """Request to refund an operation."""

    partial_amount: float | None = Field(
        default=None,
        description="Refund amount.",
    )


class RewardRequest(APIModel):
    """Request to accrue or deduct points."""

    comment: str | None = None
    points: float
    participants: list[int]
    silent: bool = False


class RewardResponse(APIModel):
    """Reward result (number of accepted participants)."""

    accepted: int = Field(
        description="Number of users who will be rewarded with points.",
    )


class CreateVoucherReceipt(APIModel):
    """Receipt for creating a voucher."""

    total: float = Field(
        description="Total receipt amount (in currency units)."
    )
    number: str | None = Field(
        default=None,
        description="Receipt number.",
    )
    skip_loyalty_total: float | None = Field(
        default=None,
        description="Part of bill amount without cashback/discount.",
    )


class CreateVoucher(APIModel):
    """Request to create a voucher."""

    nonce: str | None = Field(
        default=None,
        description="Nonce for voucher (UUID).",
    )
    cashier: CashierInput | None = None
    receipt: CreateVoucherReceipt


class VoucherInfo(APIModel):
    """Voucher information."""

    code: str = Field(description="UDS voucher code.")
    qr_code_text: str = Field(
        description="UDS voucher info for qrcode.",
    )
    qr_code_128: str = Field(
        description="Link for generate qrcode image (size 128).",
    )
    qr_code_256: str = Field(
        description="Link for generate qrcode image (size 256).",
    )
    expires_in: datetime = Field(
        description="Voucher code expires in (UTC time-zone).",
    )
    points: float = Field(description="Minimum points for withdrawal.")


class PurchaseCalcExtras(APIModel):
    """Additional purchase calculation data."""

    delivery: float | None = Field(
        default=None,
        description="Delivery cost (in currency units).",
    )


class PurchaseCalc(APIModel):
    """Purchase calculation result."""

    max_points: float | None = Field(
        default=None,
        description="Maximum number of points available.",
    )
    total: float | None = Field(
        default=None,
        description="Total bill (in currency units).",
    )
    skip_loyalty_total: float | None = Field(
        default=None,
        description="Part of bill amount without cashback/discount.",
    )
    unredeemable_total: float | None = Field(
        default=None,
        description="Part of total that cannot be redeemed with points.",
    )
    discount_amount: float | None = Field(
        default=None,
        description="Discount amount (in currency units).",
    )
    discount_percent: float | None = Field(
        default=None,
        description="Discount rate (as a percentage).",
    )
    points: float | None = Field(
        default=None,
        description="Payable points.",
    )
    points_percent: float | None = Field(
        default=None,
        description="Discount rate due to points (as a percentage).",
    )
    net_discount: float | None = Field(
        default=None,
        description="Total discount amount (in currency units).",
    )
    net_discount_percent: float | None = Field(
        default=None,
        description="Total discount rate (as a percentage of the total bill).",
    )
    certificate_points: float | None = Field(
        default=None,
        description="Number of deducted certificate points.",
    )
    cash: float | None = Field(
        default=None,
        description="Payable amount (in currency units).",
    )
    cash_total: float | None = Field(
        default=None,
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
    extras: PurchaseCalcExtras | None = Field(
        default=None,
        description=(
            "Additional payments will not be taken into account by the "
            "loyalty program."
        ),
    )
    max_scores_discount: float | None = Field(
        default=None,
        description=(
            "Maximum discount (as a percentage) allowed for redeeming points."
        ),
    )


class PurchaseCalcRequestParticipant(APIModel):
    """Participant for purchase calculation."""

    uid: str | None = None
    phone: str | None = None


class PurchaseCalcRequestReceipt(APIModel):
    """Receipt for purchase calculation."""

    total: float
    skip_loyalty_total: float | None = None
    unredeemable_total: float | None = None
    points: float | None = None


class PurchaseCalcRequest(APIModel):
    """Request to calculate a purchase."""

    code: str | None = None
    participant: PurchaseCalcRequestParticipant | None = None
    receipt: PurchaseCalcRequestReceipt
