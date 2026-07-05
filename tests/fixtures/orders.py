GOODS_ORDER_RESPONSE = {
    "id": 42,
    "dateCreated": "2024-03-01T10:00:00Z",
    "state": "NEW",
    "orderStatus": "ACCEPTED",
    "total": 1500.0,
    "cash": 1400.0,
    "points": 100.0,
    "items": [
        {
            "id": 1,
            "name": "Product A",
            "type": "ITEM",
            "qty": 2,
            "price": 750.0,
        }
    ],
    "purchase": {
        "maxPoints": 100.0,
        "total": 1500.0,
        "cash": 1400.0,
        "points": 100.0,
    },
}

GOODS_ORDER_CODE_RESPONSE = {
    "code": "123456",
}

GOODS_ORDER_COMPLETE_RESPONSE = {
    "transaction": {
        "id": 777,
    },
    "order": GOODS_ORDER_RESPONSE,
}
