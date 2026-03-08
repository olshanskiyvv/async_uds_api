from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from async_uds_api.models.orders import BranchInfo
from async_uds_api.models.customers import OperationCustomer


class CashierInfo(BaseModel):
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


class CreateVoucherCashier(BaseModel):
    external_id: Optional[str] = Field(
        default=None,
        alias="externalId",
        validation_alias="externalId",
        description="External cashier identifier.",
    )
    name: Optional[str] = Field(
        default=None,
        description="Cashier name.",
    )


class CreateVoucherReceipt(BaseModel):
    total: float = Field(description="Total receipt amount (in currency units).")
    number: Optional[str] = Field(
        default=None,
        description="Receipt number.",
    )
    skip_loyalty_total: Optional[float] = Field(
        default=None,
        alias="skipLoyaltyTotal",
        validation_alias="skipLoyaltyTotal",
        description="Part of bill amount without cashback/discount.",
    )


class CreateVoucher(BaseModel):
    nonce: Optional[str] = Field(
        default=None,
        description="Nonce for voucher (UUID).",
    )
    cashier: Optional[CreateVoucherCashier] = None
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
