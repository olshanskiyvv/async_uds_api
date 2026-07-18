## async-uds-api

Асинхронный Python-клиент для публичного UDS Partner API v2.

### Установка

```bash
pip install async-uds-api
```

### Быстрый старт

```python
import asyncio
from async_uds_api import UDSClient


async def main() -> None:
    client = UDSClient(
        company_id="123456",
        api_key="your-api-key",
    )

    async with client:
        # Получение настроек компании
        settings = await client.settings.get()
        print(settings.name, settings.currency)

        # Список клиентов
        customers = await client.customers.list(max=10, offset=0)
        for customer in customers.rows:
            print(customer.display_name, customer.phone)


if __name__ == "__main__":
    asyncio.run(main())
```

### Возможности

- **Асинхронный HTTP-клиент** на базе `httpx.AsyncClient`
- **Авторизация** через Basic Auth (`companyId:apiKey`)
- **Автоматические заголовки** `X-Origin-Request-Id` и `X-Timestamp`
- **Pydantic-модели** для валидации данных
- **Типизация** — полная поддержка статических анализаторов
- **Обработка ошибок** — иерархия исключений с детальной информацией

### API

#### Settings

```python
settings = await client.settings.get()
```

#### Customers

```python
# Список клиентов
customers = await client.customers.list(max=100, offset=0)

# Поиск клиента по коду/телефону/UID
result = await client.customers.find(code="ABC123", total=1000.0)

# Получение клиента по ID
customer = await client.customers.get(customer_id=12345)

# Теги клиента
tags = await client.customers.get_tags(customer_id=12345)
await client.customers.set_tags(customer_id=12345, tag_ids=[1, 2, 3])
```

#### Operations

```python
from async_uds_api.models import CreateOperation

# Список операций
operations = await client.operations.list(max=100)

# Создание операции (покупка/начисление)
operation = await client.operations.create(CreateOperation(...))

# Получение операции по ID
operation = await client.operations.get(operation_id=12345)

# Возврат операции
refunded = await client.operations.refund(operation_id=12345)

# Расчёт покупки
calc_result = await client.operations.calc(calc_request)

# Начисление бонусов
await client.operations.reward(reward_request)

# Создание ваучера
voucher = await client.operations.create_voucher(voucher)
```

#### Tags

```python
# Список тегов компании
tags = await client.tags.list()
```

#### Goods

```python
from async_uds_api.models import GoodsDetailed

# Список товаров
goods = await client.goods.list(max=100)

# Создание товара
new_goods = await client.goods.create(GoodsDetailed(name="Товар", ...))

# Получение по ID
item = await client.goods.get(goods_id=123)

# Обновление
updated = await client.goods.update(goods_id=123, goods=GoodsDetailed(...))

# Удаление
await client.goods.delete(goods_id=123)

# Работа с externalId
item = await client.goods.external.get(external_id="ext-123")
updated = await client.goods.external.update(external_id="ext-123", goods=...)
await client.goods.external.delete(external_id="ext-123")
```

#### Images

```python
# Загрузка изображения из файла
image_id = await client.images.upload("/path/to/image.jpg")

# Загрузка из URL
image_id = await client.images.upload("https://example.com/image.png")

# Загрузка из байтов
image_id = await client.images.upload(image_bytes, content_type="image/png")

# Получение URL для загрузки
upload_url = await client.images.get_upload_url("image/jpeg")
```

#### Goods Orders

```python
from async_uds_api import GoodsOrderUpdate, GoodsOrderUpdateStatus

# Получение заказа
order = await client.goods_orders.get(order_id=123)

# Обновление заказа (позиции, доставка)
await client.goods_orders.update(order_id=123, body=GoodsOrderUpdate(...))

# Смена статуса заказа
await client.goods_orders.change_status(
    order_id=123, status=GoodsOrderUpdateStatus.READY
)

# Отмена заказа
await client.goods_orders.cancel(order_id=123)

# Завершение заказа (создаёт транзакцию)
result = await client.goods_orders.complete(order_id=123)
result.transaction.id  # ID созданной транзакции
result.order  # GoodsOrderDetailed

# Генерация кода оплаты
code_info = await client.goods_orders.generate_code(order_id=123)
```

### Логирование

Библиотека пишет в логгер `async_uds_api` и по умолчанию ничего не выводит
(`NullHandler`). Чтобы увидеть сообщения, настройте стандартный `logging`:

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
)
logging.getLogger("async_uds_api").setLevel(logging.INFO)
```

Вывод:

```
GET /customers [max=50 cursor=abc] [X-Origin-Request-Id=6e1c89d3-...] [X-Timestamp=2026-07-18T19:59:54.981185+00:00]
GET /customers/find [phone=***4567] [X-Origin-Request-Id=6e1c89d3-...] [X-Timestamp=2026-07-18T19:59:54.981185+00:00]
GET /customers/find -> 200 OK in 0.312s
```

#### Маскирование персональных данных

В лог попадают все query-параметры запроса. Маскируются только `phone`,
`uid` и `code` — они сокращаются до последних четырёх символов и никогда
не попадают в лог целиком. Остальные параметры (например, `max`, `cursor`,
`offset`) выводятся в логе без изменений — это помогает при разборе
инцидентов.

По умолчанию `UDSClient` выставляет логгеру `httpx` уровень `WARNING`:
на уровне `INFO` httpx печатает полный URL запроса вместе с query-строкой,
то есть **незамаскированный** телефон. Отключить это поведение можно так:

```python
client = UDSClient(company_id="...", api_key="...", silence_httpx_log=False)
```

Учтите, что при `silence_httpx_log=False` номера телефонов, uid и коды клиентов
будут утекать в лог через URL запросов httpx.

#### Свой логгер

`UDSClient` принимает любой объект с методами `debug`/`info`/`warning`/`error`,
которые получают имя события и поля через `**kwargs`. `structlog` и `loguru`
подходят без обёртки:

```python
import structlog

client = UDSClient(
    company_id="...",
    api_key="...",
    logger=structlog.get_logger(),
)
```

События и их поля:

| Событие | Уровень | Поля |
|---|---|---|
| `uds.request` | INFO | `method`, `path`, `params`, `request_id`, `timestamp` |
| `uds.response` | INFO | `method`, `path`, `status`, `elapsed` |
| `uds.error` | ERROR | `method`, `path`, `status`, `elapsed`, `message`, `error_code` |
| `uds.retry` | WARNING | `method`, `path`, `attempt` |
| `uds.image.*` | DEBUG/INFO/ERROR | зависит от события |

При стандартном логгере эти поля доступны хендлерам через `record.uds` —
словарь с исходными значениями, удобный для JSON-форматтеров. Атрибут
`uds` присутствует на всех записях, которые библиотека пишет через
`StdlibLoggerAdapter`, включая события `async_uds_api.api.images`. Читать
его всё равно стоит защищённо: `getattr(record, "uds", None)`.

### Webhooks

```python
is_valid = client.verify_webhook_signature(
    request_id=request.headers.get("X-RequestId"),
    timestamp=request.headers.get("X-Timestamp"),
    signature=request.headers.get("X-Signature"),
)
```

### Обработка ошибок

```python
from async_uds_api import (
    UDSClientError,
    UDSAPIError,
    UDSBadRequestError,
    UDSUnauthorizedError,
    UDSForbiddenError,
    UDSNotFoundError,
    UDSUnexpectedError,
    UDSImageError,
)

try:
    customer = await client.customers.get(999999)
except UDSNotFoundError as e:
    print(f"Не найдено: {e.message}")
except UDSAPIError as e:
    print(f"API ошибка: {e.status_code}, {e.error_code}")
except UDSClientError as e:
    print(f"Ошибка клиента: {e}")
```

### Требования

- Python >= 3.10
- httpx >= 0.27.0
- pydantic >= 2.0.0
- aiofiles >= 23.0.0

### Разработка

```bash
# Установка зависимостей для разработки
uv sync --dev

# Запуск тестов
uv run pytest tests/

# Линтинг
uv run ruff check async_uds_api/ tests/

# Форматирование
uv run ruff format async_uds_api/ tests/

# Проверка типов
uv run mypy
```

### Лицензия

MIT
