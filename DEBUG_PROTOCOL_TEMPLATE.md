# Протокол отладки

| № |     Модуль     |           Точка               |   Ошибка/симптом    | Причина | Исправление |
|---|----------------|-------------------------------|---------------------|---------|-------------|
| 1 | DataAccess     | `BaseRepository.add`          |                     |         |             |
| 2 | BusinessLogic  | `RentalService.create_rental` |                     |         |             |
| 3 | Presentation   | `MainWindow.create_rental`    |                     |         |             |

Рекомендуемые точки останова: `RentalService.create_rental`, `RentalService.return_bike`, `BaseRepository.add`, `MainWindow.create_rental`. Следить за `bike.is_available`, `rental.id`, `client.id`, `expected_return_at`, `total_cost`.
