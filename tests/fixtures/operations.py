OPERATIONS_LIST_RESPONSE = {
    "rows": [
        {
            "id": 123,
            "dateCreated": "2024-01-01T12:00:00Z",
            "action": "PURCHASE",
            "state": "NORMAL",
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
    "state": "NORMAL",
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
