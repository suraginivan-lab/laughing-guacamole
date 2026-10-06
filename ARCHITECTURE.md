# Схема интеграции

```text
Presentation / PySide6
        ↓
Business Logic / Services / Exceptions
        ↓
Data Access / Repositories / ORM
        ↓
SQLite
```

Сквозной сценарий аренды: UI передаёт выбранные ID в `RentalService` → сервис проверяет клиента, велосипед, доступность и срок → `RentalRepository` создаёт аренду → `BikeRepository` меняет доступность → транзакция фиксируется → UI обновляет таблицы.
