from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field

from async_uds_api.models.customers import OperationCustomer
from async_uds_api.models.orders import BranchInfo


class CashierInfo(BaseModel):
    id: int
    display_name: str = Field(
        alias="displayName",
        validation_alias="displayName",
    )


class Operation(BaseModel):
    id: int | None = Field(
        default=None, description="Transaction ID in the UDS."
    )
    date_created: datetime | None = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
        description="Transaction date.",
    )
    action: str | None = None
    state: str | None = None
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


class OperationsPage(BaseModel):
    rows: list[Operation]
    total: int | None = None
    cursor: str | None = None


class CreateOperationParticipant(BaseModel):
    uid: str | None = None
    phone: str | None = None


class CreateOperationReceipt(BaseModel):
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


class CreateOperation(BaseModel):
    code: str | None = None
    participant: CreateOperationParticipant | None = None
    nonce: str | None = None
    cashier_external_id: str | None = Field(
        default=None,
        alias="cashierExternalId",
        description="External cashier identifier.",
    )
    cashier_name: str | None = Field(
        default=None,
        alias="cashierName",
        description="Cashier name.",
    )
    receipt: CreateOperationReceipt
    tags: list[int] | None = None


class RefundOperationRequest(BaseModel):
    partial_amount: float | None = Field(
        default=None,
        alias="partialAmount",
        validation_alias="partialAmount",
        description="Refund amount.",
    )


class RewardRequest(BaseModel):
    comment: str | None = None
    points: float
    participants: list[int]
    silent: bool = False


class CreateVoucherCashier(BaseModel):
    external_id: str | None = Field(
        default=None,
        alias="externalId",
        validation_alias="externalId",
        description="External cashier identifier.",
    )
    name: str | None = Field(
        default=None,
        description="Cashier name.",
    )


class CreateVoucherReceipt(BaseModel):
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


class CreateVoucher(BaseModel):
    nonce: str | None = Field(
        default=None,
        description="Nonce for voucher (UUID).",
    )
    cashier: CreateVoucherCashier | None = None
    receipt: CreateVoucherReceipt


class VoucherInfo(BaseModel):
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
