"""
Mock API responses for testing.
"""

COMPANY_SETTINGS_RESPONSE = {
    "id": 123456,
    "name": "Test Company",
    "promoCode": "TESTCOMPANY",
    "currency": "RUB",
    "baseDiscountPolicy": "POINTS",
    "purchaseByPhone": True,
    "usePointsByPhone": True,
    "writeInvoice": False,
    "slug": "test-company",
    "loyaltyProgramSettings": {
        "baseMembershipTier": {
            "uid": "base",
            "name": "Base",
            "rate": 0.05,
            "maxScoresDiscount": 50.0,
        },
        "membershipTiers": [],
        "referralCashbackRates": [0.05, 0.03, 0.01],
        "cashierAward": 0.01,
        "referralReward": 100.0,
        "discountVip": 10.0,
        "receiptLimit": 100000.0,
        "deferPointsForDays": 7,
    },
}

CUSTOMERS_LIST_RESPONSE = {
    "rows": [
        {
            "uid": "abc123",
            "displayName": "John Doe",
            "phone": "+79001234567",
            "participant": {
                "id": 123,
                "points": 100.0,
                "discountRate": 5.0,
                "cashbackRate": 3.0,
            },
        },
        {
            "uid": "def456",
            "displayName": "Jane Smith",
            "phone": "+79007654321",
        },
    ]
}

CUSTOMER_DETAIL_RESPONSE = {
    "uid": "abc123",
    "displayName": "John Doe",
    "phone": "+79001234567",
    "participant": {
        "id": 123,
        "points": 100.0,
        "discountRate": 5.0,
        "cashbackRate": 3.0,
    },
    "tags": [
        {"id": 1, "name": "VIP"},
        {"id": 2, "name": "Regular"},
    ],
}

OPERATIONS_LIST_RESPONSE = {
    "rows": [
        {
            "id": 123,
            "dateCreated": "2024-01-01T12:00:00Z",
            "action": "PURCHASE",
            "state": "COMPLETED",
            "points": 50.0,
            "total": 1000.0,
            "cash": 950.0,
        }
    ],
    "total": 1,
}

OPERATION_RESPONSE = {
    "id": 123,
    "dateCreated": "2024-01-01T12:00:00Z",
    "action": "PURCHASE",
    "state": "COMPLETED",
    "points": 50.0,
    "total": 1000.0,
    "cash": 950.0,
    "customer": {
        "id": 456,
        "displayName": "John Doe",
    },
    "origin": {
        "id": 100,
    },
}

PARTICIPANT_RESPONSE = {
    "id": 123,
    "inviterId": 456,
    "points": 100.0,
    "discountRate": 5.0,
    "cashbackRate": 3.0,
    "cashSpent": 10000.0,
    "savedFunds": 500.0,
    "invitedCount": 10,
    "effectiveInvitedCount": 5,
    "operationsCount": 20,
    "fullRefundsCount": 1,
    "note": "Test note",
    "membershipTier": {
        "uid": "vip",
        "name": "VIP",
        "rate": 10.0,
        "maxScoresDiscount": 50.0,
    },
    "dateCreated": "2023-01-01T00:00:00Z",
    "lastTransactionTime": "2024-01-01T12:00:00Z",
    "pointsExpireIn": "2025-01-01T00:00:00Z",
}

PURCHASE_CALC_RESPONSE = {
    "user": {
        "uid": "abc123",
        "displayName": "John Doe",
        "phone": "+79001234567",
        "tags": [],
    },
    "purchase": {
        "maxPoints": 100.0,
        "total": 1000.0,
        "cash": 900.0,
        "points": 100.0,
    },
    "code": "123456",
    "type": "PURCHASE",
}

TAGS_LIST_RESPONSE = {
    "rows": [
        {"id": 1, "name": "VIP"},
        {"id": 2, "name": "Regular"},
    ],
    "total": 2,
}

GOODS_LIST_RESPONSE = {
    "rows": [
        {
            "id": 1,
            "name": "Test Product",
            "data": {
                "type": "ITEM",
                "price": 100.0,
            },
            "imageUrls": ["https://example.com/image.jpg"],
        }
    ],
    "total": 1,
}

GOODS_DETAIL_RESPONSE = {
    "id": 1,
    "name": "Test Product",
    "data": {
        "type": "ITEM",
        "price": 100.0,
        "description": "Test description",
    },
    "imageUrls": ["https://example.com/image.jpg"],
}

IMAGE_UPLOAD_URL_RESPONSE = {
    "imageId": (
        "NTQ5NzU1ODIxNDg5L0dPT0RTLzdiYzBlNTU0LWMyNzMtNDc1MC05MjEyLWY0NWJhNWM1ODZiOQ=="
    ),
    "url": "https://storage.googleapis.com/test-bucket/test-image",
    "method": "PUT",
    "headers": {
        "Content-Type": ["image/jpeg"],
    },
    "expires": 1632137293751,
}

CUSTOMER_TAGS_RESPONSE = {
    "rows": [
        {"id": 1, "name": "VIP"},
        {"id": 2, "name": "Regular"},
    ],
    "total": 2,
}
