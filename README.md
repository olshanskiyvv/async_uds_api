# async-uds-api

Асинхронный Python-клиент для публичного UDS Partner API v2.

## Установка

```bash
pip install async-uds-api
```

## Быстрый старт

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

## Возможности

- **Асинхронный HTTP-клиент** на базе `httpx.AsyncClient`
- **Авторизация** через Basic Auth (`companyId:apiKey`)
- **Автоматические заголовки** `X-Origin-Request-Id` и `X-Timestamp`
- **Сквозной origin request id** — идентификатор внешней цепочки запросов
- **Pydantic-модели** для валидации данных
- **Типизация** — полная поддержка статических анализаторов
- **Обработка ошибок** — иерархия исключений с детальной информацией

## API

Ресурсы клиента и их назначение:

| Ресурс | Назначение |
|---|---|
| `client.settings` | настройки компании и программы лояльности |
| `client.customers` | клиенты: поиск, карточка, теги |
| `client.operations` | операции: расчёт, покупка, возврат, начисление/списание баллов, ваучеры |
| `client.tags` | теги компании |
| `client.goods` | товары (в т.ч. по `externalId` через `client.goods.external`) |
| `client.images` | загрузка изображений |
| `client.goods_orders` | заказы товаров |
| `client.webhooks` | вебхуки: проверка подписи и разбор payload |

Подробности по каждому методу — в docstring соответствующих классов и методов,
примеры использования — в [Сценариях](#сценарии).

## Сценарии

### Оплата (покупка)

Общий сценарий оплаты: поиск клиента → расчёт → проведение → возврат
(опционально). Покрывает оплату баллами и сертификатом — обрабатываются
одинаково, разница только в источнике списания.

**Механика баллов и сертификатов:**

- **Баллы** — накапливаются на балансе клиента (кэшбэк за покупки). Списание
  баллов уменьшает баланс.
- **Сертификат** — отдельный баланс баллов с собственным лимитом списания на одну
  покупку (вне лимита уровня лояльности). Списание сертификата не трогает обычный
  баланс баллов, а кэшбэк на оплаченную сумму всё равно поступает на обычный
  баланс.

Сначала найдите клиента, чтобы получить его `token_type` и код:

```python
# По коду из приложения — доступно списание баллов/сертификата.
found = await client.customers.find(code="950692")
found.token_type  # PURCHASE (баллы) или CERTIFICATE (сертификат)

# По телефону — только начисление (списание по телефону возможно, только если
# компания разрешила его в настройках).
found = await client.customers.find(phone="+79123456789")
```

В операции списание с баланса видно по полю `points`, с сертификата — по
`certificate_points`.

```python
from async_uds_api.models import (
    CreateOperation,
    CreateOperationReceipt,
    PurchaseCalcRequest,
    PurchaseCalcRequestReceipt,
)

# 1. Расчёт. Передаём код из приложения UDS.
calc = await client.operations.calc(
    PurchaseCalcRequest(
        code="950692",
        receipt=PurchaseCalcRequestReceipt(total=1000.0),
    )
)

# 2. Проведение операции. Передаём ровно значения calc — без самостоятельного расчёта.
op = await client.operations.create(
    CreateOperation(
        code="950692",
        receipt=CreateOperationReceipt(
            total=calc.purchase.total,
            cash=calc.purchase.cash,
            points=calc.purchase.points,
        ),
    )
)

# Опционально: возврат.
refunded = await client.operations.refund(operation_id=op.id)
refunded.state  # ActionState.REVERSAL
```

Нюансы:

- **Точность расчёта.** UDS считает в дробных баллах. Рекомендуется брать
  `total`/`cash`/`points` из ответа `calc`, а не пересчитывать их через float:
  при округлении возможна погрешность (`100.05 - 25.01 = 75.03999999999999`,
  а не `75.04`), и `create` с таким значением вернёт `400 invalidChecksum` или
  `400 badRequest`.
- **Код одноразовый.** Код из приложения расходуется после успешного `create`;
  повторное использование возвращает `404 notFound`. Для повторных операций —
  новый код или `find(code=..., exchange_code=True)` (долгосрочный код).
- **Знаки.** В операции `points` при списании отрицательный, `certificate_points`
  при списании сертификата положительный. Возврат зеркален: `points` положительный
  (баллы вернулись), `cash` и `certificate_points` отрицательные (деньги/сертификат
  вернулись).

### Заказы товаров

```python
from async_uds_api.models import GoodsOrderItemUpdate

order = await client.goods_orders.get(order_id=123)
order.state  # NEW / NEED_ACK / WAITING_PAYMENT / COMPLETED / DELETED

# Правка позиций (для VARYING_ITEM обязателен variant_name)
await client.goods_orders.update(
    order_id=123,
    items=[GoodsOrderItemUpdate(id=1, variant_name="Модуль 1", qty=2)],
)

# Подтверждение заказа с онлайн-оплатой: NEED_ACK -> WAITING_PAYMENT
await client.goods_orders.confirm(order_id=123)

# Принять заказ (order_status: None -> ACCEPTED)
await client.goods_orders.accept(order_id=123)

# Готов к выдаче (order_status: ACCEPTED -> READY)
await client.goods_orders.ready(order_id=123)

# Завершение (создаёт транзакцию)
result = await client.goods_orders.complete(order_id=123)
result.transaction.id  # созданная транзакция

# Отмена
await client.goods_orders.cancel(order_id=123)  # state=DELETED
```

Жизненный цикл заказа:

| Заказ | `state` | `order_status` |
|---|---|---|
| Требует подтверждения | `NEED_ACK` | - |
| Ожидает оплаты | `WAITING_PAYMENT` | - |
| Новый заказ | `NEW` | - |
| Принят | `NEW` | `ACCEPTED` |
| Готов к выдаче | `NEW` | `READY` |
| Выполнен | `COMPLETED` | - |
| Отменён | `DELETED` | - |

`NEED_ACK` и `WAITING_PAYMENT` доступны только при подтверждении заказа
(онлайн-оплата); заказ, полностью оплаченный баллами, приходит сразу в `NEW`.
`confirm()` переводит `NEED_ACK` → `WAITING_PAYMENT`. В состоянии `NEW` поле
`order_status` проходит цепочку `None` → `ACCEPTED` → `READY`: `None` — заказ
только создан (без статуса обработки), `accept()` ставит `ACCEPTED`, а `ready()` —
`READY`.

### Вебхуки

Вебхуки приходят в тех же моделях, что и ответы API:

| Событие | Модель |
|---|---|
| новый клиент | `Customer` |
| новая операция (не от заказа) | `Operation` |
| новый заказ | `GoodsOrderDetailed` |
| обновление заказа | `GoodsOrderDetailed` |

Подпись проверяется через `verify_webhook_signature`. Пример FastAPI-обработчика:

```python
from fastapi import FastAPI, Request

from async_uds_api import UDSClient

app = FastAPI()
client = UDSClient(company_id="...", api_key="...")


@app.post("/webhooks/goods-order")
async def on_goods_order(request: Request):
    if not client.verify_webhook_signature(
        request_id=request.headers.get("X-RequestId", ""),
        timestamp=request.headers.get("X-Timestamp", ""),
        signature=request.headers.get("X-Signature", ""),
    ):
        return {"error": "invalid signature"}, 401

    order = client.webhooks.parse_goods_order(await request.json())
    # обработайте заказ...
    return {"ok": True}
```

События «новый заказ» и «обновление заказа» — **разные вебхуки**, настраиваются
раздельно. Вебхук обновления шлёт весь заказ с обновлёнными значениями (не diff).
В openapi вебхук обновления не описан, а добавлен он недавно — актуально на
октябрь 2026.

## Логирование

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
GET /customers/find -> 200 OK in 0.312s [X-Origin-Request-Id=6e1c89d3-...] [X-Request-Id=8c828ee7-...]
```

### Маскирование персональных данных

В лог попадают все query-параметры запроса. Маскируются только `phone`,
`uid` и `code` — они сокращаются до последних четырёх символов и никогда
не попадают в лог целиком. Остальные параметры (например, `max`, `cursor`,
`offset`) выводятся в логе без изменений — это помогает при разборе
инцидентов.

Текст сообщения об ошибке, который UDS возвращает в ответе, может
содержать эхо `phone`/`uid`/`code` — иногда в нормализованном виде,
отличном от того, что было передано в запросе. Библиотека не пытается
вычищать чужой текст регулярными выражениями: она просто **никогда его
не логирует**. Событие `uds.error` не содержит поля `message`, а
`str(exc)` у `UDSAPIError` — это безопасная сводка вида
`400 for GET /customers/find [errorCode=badRequest]`.

В атрибут `exc.message` попадает **только** поле `message` из корректно
разобранного JSON-объекта ответа — это документированное поле UDS API,
его можно осознанно прочитать и, при необходимости, залогировать самому.
Любое другое тело ответа (plain text или HTML-страница от прокси, WAF или
CDN — такие страницы часто печатают запрошенный URI вместе с
незамаскированным `phone`) в `exc.message` не попадает: вместо него
используется та же безопасная сводка, что и при пустом теле
(`500 for GET /customers/find`):

```python
except UDSAPIError as e:
    print(e)          # 400 for GET /customers/find [errorCode=badRequest]
    print(e.message)  # поле message из JSON UDS, может содержать ПДн
```

То же относится и к `httpx.HTTPStatusError`, который остаётся в
`__cause__` у ошибок API-запросов: его собственный текст содержит полный
URL запроса вместе с query-строкой, поэтому он переписывается на сводку
вида `400 for GET /customers/find` — без query-строки, а значит без
`phone`/`uid`/`code`. Тип исключения и его `.response` не меняются.
Благодаря этому телефон не появляется и в полном traceback, который
печатает `logging.exception`.

Это правило касается только запросов к API UDS. URL в путях загрузки
изображений (presigned-ссылки и адрес источника) не маскируются: они
короткоживущие, а без полного URL непонятно, какой именно объект не
загрузился. Сообщения и traceback этих путей содержат исходный URL
целиком.

`mask_value` и `mask_params` экспортируются из `async_uds_api` — ими
можно пользоваться и вне библиотеки, например в собственных логах.

По умолчанию `UDSClient` выставляет логгеру `httpx` уровень `WARNING`:
на уровне `INFO` httpx печатает полный URL запроса вместе с query-строкой,
то есть **незамаскированный** телефон. Отключить это поведение можно так:

```python
client = UDSClient(company_id="...", api_key="...", silence_httpx_log=False)
```

Учтите, что при `silence_httpx_log=False` номера телефонов, uid и коды клиентов
будут утекать в лог через URL запросов httpx.

### Свой логгер

`UDSClient` принимает любой объект с методами `debug`/`info`/`warning`/`error`,
которые получают имя события и поля через `**kwargs`. `structlog` и `loguru`
поддерживаются без обёртки:

```python
import structlog

client = UDSClient(
    company_id="...",
    api_key="...",
    logger=structlog.get_logger(),
)
```

Также можно передать обычный `logging.Logger` или `logging.LoggerAdapter` —
оба автоматически оборачиваются в `StdlibLoggerAdapter`, так что классический
формат сообщений (см. пример вывода выше) сохраняется и для `LoggerAdapter`:

```python
import logging

client = UDSClient(
    company_id="...",
    api_key="...",
    logger=logging.LoggerAdapter(logging.getLogger("myapp"), {}),
)
```

Если переданный объект не является ни `Logger`/`LoggerAdapter`, ни
объектом с методами `debug`/`info`/`warning`/`error`, `UDSClient` бросает
`TypeError` уже в конструкторе — до того, как логирование сломает первый
же запрос.

События и их поля:

| Событие | Уровень | Поля |
|---|---|---|
| `uds.request` | INFO | `method`, `path`, `params`, `request_id`, `timestamp` |
| `uds.response` | INFO | `method`, `path`, `status`, `elapsed`, `request_id`, `uds_request_id` |
| `uds.error` | ERROR | `method`, `path`, `status`, `elapsed`, `error_code`, `request_id`, `uds_request_id` |
| `uds.retry` | WARNING | `method`, `path`, `attempt` |
| `uds.image.*` | DEBUG/INFO/ERROR | зависит от события |

Поле `request_id` — это значение, которое клиент отправил в
`X-Origin-Request-Id`. Поле `uds_request_id` — значение заголовка
`X-Request-Id`, которым сервер UDS пометил запрос у себя; оно равно
`None`, если сервер заголовок не прислал.

События `uds.image.*` пишут URL как есть: поле `url` у
`uds.image.download_start`, `uds.image.download_done` и
`uds.image.download_failed`, поле `source` у
`uds.image.upload_start_source`, а также тексты `UDSImageDownloadError`
и `UDSImageUploadError` содержат полный URL. Это осознанный выбор:
presigned-ссылки короткоживущие, а `https://cdn.example.com/***` не
говорит, какой объект не загрузился. Если такие URL не должны попадать
в ваш лог, отфильтруйте эти события на стороне хендлера.

При стандартном логгере эти поля доступны хендлерам через `record.uds` —
словарь с исходными значениями, удобный для JSON-форматтеров. Атрибут
`uds` присутствует на всех записях, которые библиотека пишет через
`StdlibLoggerAdapter`, включая события `async_uds_api.api.images`. Читать
его всё равно стоит защищённо: `getattr(record, "uds", None)`.

### Диагностика логирования

Логирование никогда не должно ронять запрос: если пользовательский
обработчик логов бросает исключение, `StdlibLoggerAdapter` по умолчанию
молча его глотает. Чтобы увидеть это исключение при отладке, выставьте
переменную окружения `ASYNC_UDS_API_DEBUG_LOGGING` в любое непустое
значение — тогда исключение из обработчика будет пробрасываться наружу:

```bash
export ASYNC_UDS_API_DEBUG_LOGGING=1
```

## Сквозной origin request id

По умолчанию клиент генерирует `X-Origin-Request-Id` сам — новый UUID на
каждый HTTP-запрос. Чтобы связать вызовы UDS с трассировкой вашего
сервиса, передайте идентификатор цепочки одним из трёх способов.

**Параметр метода** — точечно, для одного вызова:

```python
await client.customers.find(phone="+79991234567", request_id="trace-42")
```

**Контекстный менеджер** — на блок кода:

```python
from async_uds_api import use_origin_request_id

with use_origin_request_id("trace-42"):
    await client.customers.find(phone="+79991234567")
    await client.operations.create(operation)
```

### Значение не валидируется

Библиотека передаёт значение в заголовок как есть: требования UUID нет,
подойдёт любая строка. Санитизация — ответственность вызывающей стороны.
Что важно проверить, если идентификатор приходит из входящего
HTTP-заголовка:

- символы вне ASCII (кириллица, эмодзи) приводят к `UnicodeEncodeError`
  в глубине httpx при отправке запроса;
- символы `\r` и `\n` внутри значения не дают провести header injection
  в исходящий запрос: httpx/h11 отбивают такое значение как
  недопустимое (`LocalProtocolError: Illegal header value`), и запрос
  не уходит вовсе. Но значение попадает в лог события `uds.request` ДО
  отправки — многострочное значение позволяет подделать строки в логе
  вызывающего сервиса;
- длина не ограничивается — слишком длинное значение может быть
  отвергнуто сервером.

**`set`/`reset`** — когда вход и выход из контекста разнесены по разным
функциям, например в middleware. Значение здесь приходит из заголовка,
подконтрольного внешнему клиенту, поэтому перед передачей в
`set_origin_request_id` из него остаются только печатные ASCII-символы, а
длина обрезается. Это закрывает сразу все три риска из списка выше: и
`UnicodeEncodeError` на кириллице и эмодзи, и `LocalProtocolError` на
управляющих символах, и неограниченную длину:

```python
from async_uds_api import reset_origin_request_id, set_origin_request_id


@app.middleware("http")
async def bind_request_id(request, call_next):
    raw = request.headers.get("X-Correlation-Id", "")
    value = "".join(c for c in raw if " " <= c <= "~")[:200] or None
    token = set_origin_request_id(value)
    try:
        return await call_next(request)
    finally:
        reset_origin_request_id(token)
```

Приоритет источников: параметр метода → контекстная переменная →
сгенерированный UUID. Пустая строка на любом уровне считается «не
задано» и передаёт управление следующему уровню.

Одно значение уходит на все запросы внутри блока, включая повторные
попытки после ошибок. Спецификация UDS рекомендует уникальный
идентификатор на каждый запрос, но на обработку запроса повторное
значение не влияет — оно используется для поддержки и разбора инцидентов.

Три места, где `request_id` работает не так, как можно ожидать:

- `images.upload()` передаёт идентификатор только в запрос к UDS за
  presigned-ссылкой. Сама загрузка идёт в сторонний storage и заголовок
  не несёт.
- `settings.get()` при попадании в TTL-кэш не делает HTTP-запрос, и
  `request_id` ни на что не влияет.
- `iter_all()` у `customers`/`goods`/`operations` шлёт одно и то же
  значение на каждую страницу, только если `request_id` передан явным
  параметром метода. Значение, установленное через
  `use_origin_request_id`, так не работает: async-генератор не
  копирует контекст блока, в котором был создан, поэтому страницы,
  вытянутые после выхода из `with`, получают новый сгенерированный
  uuid4.

### Три разных request id

В HTTP-заголовках и API используются три разных идентификатора; они
различаются именем заголовка и направлением передачи:

| Идентификатор | HTTP-заголовок | Имя в API и логах |
|---|---|---|
| Трассировочный id цепочки запросов (отправляется клиентом) | `X-Origin-Request-Id` (исходящий) | параметр `request_id=`, `use_origin_request_id()`, `set_origin_request_id()`, поле лога `request_id` |
| id запроса, присвоенный на стороне UDS (в ответе) | `X-Request-Id` | поле лога `uds_request_id` |
| id входящего вебхука UDS | `X-RequestId` (без дефиса) | параметр `verify_webhook_signature(request_id=...)` |

## Обработка ошибок

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

`str(e)` у `UDSAPIError` — это безопасная сводка (`404 for GET
/customers/999999`), пригодная для логирования. Текст, который вернул
сервер, лежит в `e.message` и может содержать персональные данные:
читайте его осознанно и не пишите в лог не подумав. Подробнее — в
разделе [Маскирование персональных данных](#маскирование-персональных-данных).

## Требования

- Python >= 3.10
- httpx >= 0.27.0
- pydantic >= 2.0.0
- aiofiles >= 23.0.0

## Разработка

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

## Лицензия

MIT
