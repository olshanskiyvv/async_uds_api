## async-uds-api

Асинхронный Python-клиент для публичного UDS Partner API v2.

### Установка

После публикации пакет можно будет установить через `pip`:

```bash
pip install async-uds-api
```

А пока можно использовать библиотеку из исходников:

```bash
pip install -e .
```

### Быстрый старт

```python
import asyncio
from async_uds_api import UDSClient


async def main() -> None:
    client = UDSClient(
        company_id=123456,
        api_key="your-api-key",
    )

    async with client:
        settings = await client.get_settings()
        print(settings.name, settings.currency)

        customers_page = await client.list_customers(max=10, offset=0)
        for customer in customers_page.rows:
            print(customer.display_name, customer.phone)


if __name__ == "__main__":
    asyncio.run(main())
```

### Возможности (первоначальная версия)

- **Асинхронный HTTP-клиент** на базе `httpx.AsyncClient`;
- **Авторизация** через Basic Auth (`companyId:apiKey`);
- **Автоматические заголовки** `X-Origin-Request-Id` и `X-Timestamp`;
- **Pydantic-модели** для ключевых сущностей (`CompanySettings`, `Customer` и др.);
- Первые методы:
  - `get_settings` — `GET /settings`;
  - `list_customers` — `GET /customers`.

