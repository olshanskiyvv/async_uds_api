from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import Field

from async_uds_api.models.base import APIModel
from async_uds_api.models.common import BranchInfo, ParticipantShortInfo
from async_uds_api.models.enums import Action, ActionState

if TYPE_CHECKING:
    from async_uds_api.models.customers import CustomerDetail


class OperationCustomer(ParticipantShortInfo):
    uid: str | None = None


class CashierInfo(APIModel):
    id: int
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
    )


class OperationOrigin(APIModel):
    id: int | None = None


class Operation(APIModel):
    id: int | None = Field(
        default=None, description="Transaction ID in the UDS."
    )
    date_created: datetime | None = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
        description="Transaction date.",
    )
    action: Action
    state: ActionState | None = None
    customer: OperationCustomer | None = None
    cashier: CashierInfo | None = None
    branch: BranchInfo | None = None
    points: float | None = None
    certificate_points: float | None = Field(
        default=None,
        alias="certificatePoints",
        validation_alias="certificatePoints",
    )
    receipt_number: str | None = Field(
        default=None,
        alias="receiptNumber",
        validation_alias="receiptNumber",
    )
    origin: OperationOrigin | None = None
    total: float | None = None
    cash: float | None = None


class OperationsPage(APIModel):
    rows: list[Operation]
    total: int | None = None
    cursor: str | None = None


class CreateOperationParticipant(APIModel):
    uid: str | None = None
    phone: str | None = None


class CashierInput(APIModel):
    external_id: str = Field(
        alias="externalId",
        validation_alias="externalId",
    )
    name: str | None = None


class CreateOperationReceipt(APIModel):
    total: float
    cash: float
    points: float
    number: str | None = None
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


class CreateOperation(APIModel):
    code: str | None = None
    participant: CreateOperationParticipant | None = None
    nonce: str | None = None
    cashier: CashierInput | None = None
    receipt: CreateOperationReceipt
    tags: list[int] | None = None


class RefundOperationRequest(APIModel):
    partial_amount: float | None = Field(
        default=None,
        alias="partialAmount",
        validation_alias="partialAmount",
        description="Refund amount.",
    )


class RewardRequest(APIModel):
    comment: str | None = None
    points: float
    participants: list[int]
    silent: bool = False


class CreateVoucherReceipt(APIModel):
    total: float = Field(
        description="Total receipt amount (in currency units)."
    )
    number: str | None = Field(
        default=None,
        description="Receipt number.",
    )
    skip_loyalty_total: float | None = Field(
        default=None,
        alias="skipLoyaltyTotal",
        validation_alias="skipLoyaltyTotal",
        description="Part of bill amount without cashback/discount.",
    )


class CreateVoucher(APIModel):
    nonce: str | None = Field(
        default=None,
        description="Nonce for voucher (UUID).",
    )
    cashier: CashierInput | None = None
    receipt: CreateVoucherReceipt


class VoucherInfo(APIModel):
    code: str = Field(description="UDS voucher code.")
    qr_code_text: str = Field(
        alias="qrCodeText",
        validation_alias="qrCodeText",
        description="UDS voucher info for qrcode.",
    )
    qr_code_128: str = Field(
        alias="qrCode128",
        validation_alias="qrCode128",
        description="Link for generate qrcode image (size 128).",
    )
    qr_code_256: str = Field(
        alias="qrCode256",
        validation_alias="qrCode256",
        description="Link for generate qrcode image (size 256).",
    )
    expires_in: datetime = Field(
        alias="expiresIn",
        validation_alias="expiresIn",
        description="Voucher code expires in (UTC time-zone).",
    )
    points: float = Field(description="Minimum points for withdrawal.")


class PurchaseCalcExtras(APIModel):
    delivery: float | None = Field(
        default=None,
        description="Delivery cost (in currency units).",
    )


class PurchaseCalc(APIModel):
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
    extras: PurchaseCalcExtras | None = Field(
        default=None,
        description=(
            "Additional payments will not be taken into account by the "
            "loyalty program."
        ),
    )
    max_scores_discount: float | None = Field(
        default=None,
        alias="maxScoresDiscount",
        validation_alias="maxScoresDiscount",
        description=(
            "Maximum discount (as a percentage) allowed for redeeming points."
        ),
    )


class PurchaseCalcRequestParticipant(APIModel):
    uid: str | None = None
    phone: str | None = None


class PurchaseCalcRequestReceipt(APIModel):
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


class PurchaseCalcRequest(APIModel):
    code: str | None = None
    participant: PurchaseCalcRequestParticipant | None = None
    receipt: PurchaseCalcRequestReceipt


class PurchaseCalcResponse(APIModel):
    user: CustomerDetail
    purchase: PurchaseCalc | None = None
