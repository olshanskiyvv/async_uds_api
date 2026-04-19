from __future__ import annotations

from datetime import datetime
from typing import Annotated, Literal

from pydantic import Field

from async_uds_api.models.base import APIModel
from async_uds_api.models.enums import (
    GoodsMeasurement,
    PaymentSubject,
    VatCode,
)


class GoodsOffer(APIModel):
    offer_price: float | None = Field(
        default=None,
        description="Discount price.",
    )
    skip_loyalty: bool = Field(
        default=False,
        description=(
            "Flag of goods item price which cashback is not credited and "
            "to which the discount does not apply."
        ),
    )


class GoodsInventory(APIModel):
    in_stock: int | None = Field(
        default=None,
        description=(
            "Item quantity in stock. The 'null' value means unlimited "
            "quantity."
        ),
    )


class GoodsVariantType(APIModel):
    name: str = Field(description="Variant name.")
    sku: str | None = Field(
        default=None,
        description="Variant stock number.",
    )
    price: float = Field(description="Variant price.")
    offer: GoodsOffer | None = None
    inventory: GoodsInventory | None = None


class GoodsCategoryType(APIModel):
    type: Literal["CATEGORY"] = "CATEGORY"


class GoodsItemType(APIModel):
    type: Literal["ITEM"] = "ITEM"
    sku: str | None = Field(default=None, description="Item stock number.")
    price: float = Field(description="Item price.")
    description: str | None = Field(
        default=None, description="Item description."
    )
    offer: GoodsOffer | None = None
    inventory: GoodsInventory | None = None
    photos: list[str] = Field(
        default_factory=list,
        description="Array of image identifiers.",
    )
    measurement: GoodsMeasurement | None = Field(
        default=None,
        description="Goods measurement.",
    )
    increment: float | None = Field(
        default=None,
        description=(
            "Amount of the item that the buyer can increase or decrease "
            "by 1 interval."
        ),
    )
    min_quantity: float | None = Field(
        default=None,
        description="Minimal quantity of item for order.",
    )
    vat_code: VatCode | None = Field(
        default=None,
        description="VAT rate code.",
    )
    payment_subject: PaymentSubject | None = Field(
        default=None,
        description="Payment item attribute.",
    )


class GoodsVaryingItemType(APIModel):
    type: Literal["VARYING_ITEM"] = "VARYING_ITEM"
    variants: list[GoodsVariantType] | None = Field(
        default=None,
        description="Variants of item.",
    )
    description: str | None = Field(
        default=None, description="Variant description."
    )
    photos: list[str] = Field(
        default_factory=list,
        description="Array of image identifiers.",
    )
    vat_code: VatCode | None = Field(
        default=None,
        description="VAT rate code.",
    )
    payment_subject: PaymentSubject | None = Field(
        default=None,
        description="Payment item attribute.",
    )


GoodsData = Annotated[
    GoodsCategoryType | GoodsItemType | GoodsVaryingItemType,
    Field(discriminator="type"),
]


class GoodsInfoType(APIModel):
    id: int | None = Field(default=None, description="Goods ID in the UDS.")
    name: str = Field(description="Goods name.")
    data: GoodsData
    hidden: bool | None = Field(
        default=None, description="Is the goods hidden."
    )
    blocked: bool | None = Field(
        default=None,
        description="Is the goods blocked.",
    )
    node_id: int | None = Field(
        default=None,
        description="ID of the category in which the product is included.",
    )
    image_urls: list[str] = Field(
        default_factory=list,
        description="Array of links to item image.",
    )
    external_id: str | None = Field(
        default=None,
        description="External goods identifier.",
    )
    date_created: datetime | None = Field(
        default=None,
        description="Date item created.",
    )


class GoodsDetailed(GoodsInfoType):
    """Extended goods info with purchase calculation data."""

    pass


class GoodsPage(APIModel):
    rows: list[GoodsInfoType] = Field(
        default_factory=list,
        description="Goods information.",
    )
    total: int = Field(default=0, description="Goods amount.")
