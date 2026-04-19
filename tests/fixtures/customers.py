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
}

FIND_CUSTOMER_RESPONSE = {
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

CUSTOMER_TAGS_RESPONSE = {
    "rows": [
        {"id": 1, "name": "VIP"},
        {"id": 2, "name": "Regular"},
    ],
    "total": 2,
}
