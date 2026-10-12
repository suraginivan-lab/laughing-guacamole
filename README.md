# Прокат велосипедов

Полный учебный проект на Python 3.12+, PySide6, SQLAlchemy и SQLite.

## Возможности
- категории и велосипеды;
- регистрация клиентов;
- оформление и возврат аренды;
- расчёт стоимости по часам;
- запрет аренды занятого велосипеда;
- история и активные аренды;
- пользовательские исключения;
- логирование в `logs/app.log`;
- автоматическое создание БД и демо-данных.

## Архитектура
`presentation` → `business_logic` → `data_access` → SQLite. UI не работает с БД напрямую.

## Запуск
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
python main.py
```
## Запуск тестирования
```bash
python -m pytest
```


При первом запуске автоматически создаются `bike_rental.db`, таблицы, несколько велосипедов и клиентов.

