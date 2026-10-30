from __future__ import annotations

from enum import Enum


class Gender(str, Enum):
    """Customer gender."""

    MALE = "MALE"
    FEMALE = "FEMALE"
    NOT_SPECIFIED = "NOT_SPECIFIED"


class PurchaseTokenAction(str, Enum):
    """Purchase token type (points or certificate)."""

    PURCHASE = "PURCHASE"
    BONUS_ITEMS_PURCHASE = "BONUS_ITEMS_PURCHASE"
    GOODS_ORDER_COMPLETE = "GOODS_ORDER_COMPLETE"
    CERTIFICATE = "CERTIFICATE"


class Action(str, Enum):
    """Operation type."""

    PURCHASE = "PURCHASE"
    GOODS_PURCHASE = "GOODS_PURCHASE"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> Action:
        return cls.UNKNOWN


class ActionState(str, Enum):
    """Operation state."""

    NORMAL = "NORMAL"
    CANCELED = "CANCELED"
    REVERSAL = "REVERSAL"


class GoodsType(str, Enum):
    """Goods type."""

    CATEGORY = "CATEGORY"
    ITEM = "ITEM"
    VARYING_ITEM = "VARYING_ITEM"


class GoodsMeasurement(str, Enum):
    """Goods measurement unit."""

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
    """VAT rate code."""

    NO_NDS = "NO_NDS"
    NDS_0 = "NDS_0"
    NDS_10 = "NDS_10"
    NDS_20 = "NDS_20"
    NDS_10_110 = "NDS_10_110"
    NDS_20_120 = "NDS_20_120"


class PaymentSubject(str, Enum):
    """Payment subject (Chestny ZNAK)."""

    COMMODITY = "COMMODITY"
    EXCISE = "EXCISE"
    SERVICE = "SERVICE"


class GoodsOrderState(str, Enum):
    """Goods order state."""

    NEW = "NEW"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"
    WAITING_PAYMENT = "WAITING_PAYMENT"
    NEED_ACK = "NEED_ACK"


class GoodsOrderUpdateStatus(str, Enum):
    """Order processing status set by the seller."""

    ACCEPTED = "ACCEPTED"
    READY = "READY"
    WAITING_PAYMENT = "WAITING_PAYMENT"


class GoodsOrderItemType(str, Enum):
    """Goods order item type."""

    ITEM = "ITEM"
    VARYING_ITEM = "VARYING_ITEM"


class DeliveryTypes(str, Enum):
    """Order fulfilment method."""

    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


class PaymentProvider(str, Enum):
    """Payment provider."""

    B2P = "B2P"
    CLOUD_PAYMENTS = "CLOUD_PAYMENTS"
    YOOKASSA = "YOOKASSA"
    PAYTURE = "PAYTURE"
    CUSTOM = "CUSTOM"


class PaymentType(str, Enum):
    """Payment type."""

    BEST_TO_PAY = "BEST_TO_PAY"
    CLOUD_PAYMENTS = "CLOUD_PAYMENTS"
    CASH = "CASH"
    MANUAL = "MANUAL"
    CUSTOM = "CUSTOM"


class BaseDiscountPolicy(str, Enum):
    """Company's discount method."""

    APPLY_DISCOUNT = "APPLY_DISCOUNT"
    CHARGE_SCORES = "CHARGE_SCORES"


class TaxSystemCode(str, Enum):
    """Taxation system code."""

    OSN = "OSN"
    USN_INCOME = "USN_INCOME"
    USN_INCOME_EXPENSES = "USN_INCOME_EXPENSES"
    ENVD = "ENVD"
    ESN = "ESN"
    PSN = "PSN"
