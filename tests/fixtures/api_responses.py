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
        },
        "membershipTiers": [],
        "referralCashbackRates": [0.05, 0.03, 0.01],
    },
}

CUSTOMERS_LIST_RESPONSE = {
    "rows": [
        {
            "uid": "abc123",
            "displayName": "John Doe",
            "phone": "+79001234567",
            "participant": {
                "uid": "participant123",
                "scores": 100.0,
                "cash": 500.0,
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
        "uid": "participant123",
        "scores": 100.0,
        "cash": 500.0,
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
    "customer": {
        "id": 456,
        "displayName": "John Doe",
    },
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
