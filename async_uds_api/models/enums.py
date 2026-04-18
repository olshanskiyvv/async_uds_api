from enum import Enum


class Gender(str, Enum):
    MALE = "MALE"
    FEMALE = "FEMALE"
    NOT_SPECIFIED = "NOT_SPECIFIED"


class PurchaseTokenAction(str, Enum):
    PURCHASE = "PURCHASE"
    BONUS_ITEMS_PURCHASE = "BONUS_ITEMS_PURCHASE"
    GOODS_ORDER_COMPLETE = "GOODS_ORDER_COMPLETE"
    CERTIFICATE = "CERTIFICATE"


class Action(str, Enum):
    PURCHASE = "PURCHASE"


class ActionState(str, Enum):
    NORMAL = "NORMAL"
    CANCELED = "CANCELED"
    REVERSAL = "REVERSAL"


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


class GoodsOrderState(str, Enum):
    NEW = "NEW"
    COMPLETED = "COMPLETED"
    DELETED = "DELETED"
    WAITING_PAYMENT = "WAITING_PAYMENT"
    NEED_ACK = "NEED_ACK"


class GoodsOrderUpdateStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    READY = "READY"


class GoodsOrderItemType(str, Enum):
    ITEM = "ITEM"
    VARYING_ITEM = "VARYING_ITEM"


class DeliveryTypes(str, Enum):
    PICKUP = "PICKUP"
    DELIVERY = "DELIVERY"


class PaymentProvider(str, Enum):
    B2P = "B2P"
    CLOUD_PAYMENTS = "CLOUD_PAYMENTS"
    YOOKASSA = "YOOKASSA"
    PAYTURE = "PAYTURE"
    CUSTOM = "CUSTOM"


class PaymentType(str, Enum):
    BEST_TO_PAY = "BEST_TO_PAY"
    CLOUD_PAYMENTS = "CLOUD_PAYMENTS"
    CASH = "CASH"
    MANUAL = "MANUAL"
    CUSTOM = "CUSTOM"


class BaseDiscountPolicy(str, Enum):
    APPLY_DISCOUNT = "APPLY_DISCOUNT"
    CHARGE_SCORES = "CHARGE_SCORES"


class TaxSystemCode(str, Enum):
    OSN = "OSN"
    USN_INCOME = "USN_INCOME"
    USN_INCOME_EXPENSES = "USN_INCOME_EXPENSES"
    ENVD = "ENVD"
    ESN = "ESN"
    PSN = "PSN"
