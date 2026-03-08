from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field


class GoodsType(str, Enum):
    CATEGORY = "CATEGORY"
    ITEM = "ITEM"
    VARYING_ITEM = "VARYING_ITEM"


class GoodsMeasurement(str, Enum):
    PIECE = "PIECE"
    CENTIMETRE = "CENTIMETRE"
    METRE = "METRE"
    MILLILITRE = "MILLILITRE"
    LITRE = "LITRE"
    GRAM = "GRAM"
    KILOGRAM = "KILOGRAM"
    TON = "TON"
    SQUARE_METRE = "SQUARE_METRE"
    CUBIC_METRE = "CUBIC_METRE"
    DAY = "DAY"
    HOUR = "HOUR"
    MINUTE = "MINUTE"
    KILOMETRE = "KILOMETRE"


class VatCode(str, Enum):
    NO_NDS = "NO_NDS"
    NDS_0 = "NDS_0"
    NDS_10 = "NDS_10"
    NDS_20 = "NDS_20"
    NDS_10_110 = "NDS_10_110"
    NDS_20_120 = "NDS_20_120"


class PaymentSubject(str, Enum):
    COMMODITY = "COMMODITY"
    EXCISE = "EXCISE"
    SERVICE = "SERVICE"


class GoodsOffer(BaseModel):
    offer_price: Optional[float] = Field(
        default=None,
        alias="offerPrice",
        validation_alias="offerPrice",
        description="Discount price.",
    )
    skip_loyalty: Optional[bool] = Field(
        default=None,
        alias="skipLoyalty",
        validation_alias="skipLoyalty",
        description="Flag of goods item price which cashback is not credited and to which the discount does not apply.",
    )


class GoodsInventory(BaseModel):
    in_stock: Optional[int] = Field(
        default=None,
        alias="inStock",
        validation_alias="inStock",
        description="Item quantity in stock. The 'null' value means unlimited quantity.",
    )


class GoodsVariantType(BaseModel):
    name: Optional[str] = Field(default=None, description="Variant name.")
    sku: Optional[str] = Field(
        default=None,
        description="Variant stock number.",
    )
    price: Optional[float] = Field(default=None, description="Variant price.")
    offer: Optional[GoodsOffer] = None
    inventory: Optional[GoodsInventory] = None


class GoodsCategoryType(BaseModel):
    type: GoodsType = GoodsType.CATEGORY


class GoodsItemType(BaseModel):
    type: GoodsType = GoodsType.ITEM
    sku: Optional[str] = Field(default=None, description="Item stock number.")
    price: Optional[float] = Field(default=None, description="Item price.")
    description: Optional[str] = Field(default=None, description="Item description.")
    offer: Optional[GoodsOffer] = None
    inventory: Optional[GoodsInventory] = None
    photos: Optional[List[str]] = Field(
        default=None,
        description="Array of image identifiers.",
    )
    measurement: Optional[GoodsMeasurement] = Field(
        default=None,
        description="Goods measurement.",
    )
    increment: Optional[float] = Field(
        default=None,
        description="Amount of the item that the buyer can increase or decrease by 1 interval.",
    )
    min_quantity: Optional[float] = Field(
        default=None,
        alias="minQuantity",
        validation_alias="minQuantity",
        description="Minimal quantity of item for order.",
    )
    vat_code: Optional[VatCode] = Field(
        default=None,
        alias="vatCode",
        validation_alias="vatCode",
        description="VAT rate code.",
    )
    payment_subject: Optional[PaymentSubject] = Field(
        default=None,
        alias="paymentSubject",
        validation_alias="paymentSubject",
        description="Payment item attribute.",
    )


class GoodsVaryingItemType(BaseModel):
    type: GoodsType = GoodsType.VARYING_ITEM
    variants: Optional[List[GoodsVariantType]] = Field(
        default=None,
        description="Variants of item.",
    )
    description: Optional[str] = Field(default=None, description="Variant description.")
    photos: Optional[List[str]] = Field(
        default=None,
        description="Array of image identifiers.",
    )
    vat_code: Optional[VatCode] = Field(
        default=None,
        alias="vatCode",
        validation_alias="vatCode",
        description="VAT rate code.",
    )
    payment_subject: Optional[PaymentSubject] = Field(
        default=None,
        alias="paymentSubject",
        validation_alias="paymentSubject",
        description="Payment item attribute.",
    )


GoodsData = Union[GoodsCategoryType, GoodsItemType, GoodsVaryingItemType]


class GoodsInfoType(BaseModel):
    id: Optional[int] = Field(default=None, description="Goods ID in the UDS.")
    name: str = Field(description="Goods name.")
    data: GoodsData
    hidden: Optional[bool] = Field(default=None, description="Is the goods hidden.")
    blocked: Optional[bool] = Field(
        default=None,
        description="Is the goods blocked.",
    )
    node_id: Optional[int] = Field(
        default=None,
        alias="nodeId",
        validation_alias="nodeId",
        description="ID of the category in which the product is included.",
    )
    image_urls: Optional[List[str]] = Field(
        default=None,
        alias="imageUrls",
        validation_alias="imageUrls",
        description="Array of links to item image.",
    )
    external_id: Optional[str] = Field(
        default=None,
        alias="externalId",
        validation_alias="externalId",
        description="External goods identifier.",
    )
    date_created: Optional[datetime] = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
        description="Date item created.",
    )


class GoodsDetailed(BaseModel):
    name: str = Field(description="Goods name.")
    data: GoodsData
    id: Optional[int] = Field(default=None, description="Goods ID in the UDS.")
    node_id: Optional[int] = Field(
        default=None,
        alias="nodeId",
        validation_alias="nodeId",
        description="ID of the category in which the item is included.",
    )
    external_id: Optional[str] = Field(
        default=None,
        alias="externalId",
        validation_alias="externalId",
        description="External goods identifier.",
    )
    date_created: Optional[datetime] = Field(
        default=None,
        alias="dateCreated",
        validation_alias="dateCreated",
        description="Date item created.",
    )
    hidden: Optional[bool] = Field(default=None, description="Is the goods hidden.")
    blocked: Optional[bool] = Field(
        default=None,
        description="Is the goods blocked.",
    )
    image_urls: Optional[List[str]] = Field(
        default=None,
        alias="imageUrls",
        validation_alias="imageUrls",
        description="Array of links to item image.",
    )


class GoodsPage(BaseModel):
    rows: List[GoodsInfoType] = Field(
        default_factory=list,
        description="Goods information.",
    )
    total: int = Field(default=0, description="Goods amount.")
