# Changelog

Все заметные изменения этого проекта документируются в этом файле.
Формат основан на [Keep a Changelog](https://keepachangelog.com/ru/1.1.0/),
версии следуют [Semantic Versioning](https://semver.org/lang/ru/).

## [0.2.0] - 2026-10-31

### Breaking Changes

- `goods_orders.update()` — сигнатура заменена на
  `update(order_id, *, delivery_case, items)`. Параметры `order_status` и
  `comment` удалены (их не было в схеме `GoodsOrderUpdate`).
- `operations.reward()` теперь возвращает `RewardResponse` (поле `accepted`),
  а не `None`.

### Added

- Шорткаты статусов заказа: `goods_orders.confirm()`, `.accept()`, `.ready()`.
- Сервис вебхуков `client.webhooks`:
  - `verify_signature()` — проверка подписи;
  - `parse_participant()`, `parse_operation()`, `parse_goods_order()` —
    разбор payload (`dict` или `str`) в модель.
  - `UDSClient.verify_webhook_signature()` оставлен как алиас.
- Новые поля моделей: `MembershipTier.system`,
  `OperationCustomer.membership_tier`, `GoodsOrderDetailed.external_order`,
  `GoodsOrderItem.{data_matrix_codes, delivery_state, weight_grams, width_cm,
  height_cm, length_cm}`.
- Новые модели: `ExternalOrder`, `DeliveryState`, `RewardResponse`.
- `GoodsOrderUpdateStatus.WAITING_PAYMENT`.

### Documentation

- README: раздел «Сценарии» (оплата, заказы товаров, вебхуки) и краткий
  справочник ресурсов.
- Докстринги всех публичных классов и функций.
- Актуальный openapi: русский (основной) и английский.

### Tests

- 379 тестов: разбор 63 обезличенных fixtures, сценарные и API-тесты,
  тесты шорткатов и вебхуков.
