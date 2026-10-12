from __future__ import annotations

import logging

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStatusBar,
    QTabWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from business_logic import BikeRentalError
from .dialogs import BikeDialog, CategoryDialog, ClientDialog, RentalDialog

logger = logging.getLogger(__name__)


def create_table(headers: list[str]) -> QTableWidget:
    """Создать таблицу только для чтения с выбором целой строки."""
    table = QTableWidget(0, len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
    table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
    table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
    table.horizontalHeader().setStretchLastSection(True)
    return table


class MainWindow(QMainWindow):
    """Главное окно системы проката велосипедов."""

    def __init__(self, category_service, bike_service, client_service, rental_service):
        super().__init__()
        self.category_service = category_service
        self.bike_service = bike_service
        self.client_service = client_service
        self.rental_service = rental_service

        self.setWindowTitle("Прокат велосипедов")
        self.resize(1050, 650)
        self.setStatusBar(QStatusBar())

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.bikes = create_table(
            ["ID", "Инв. №", "Марка", "Модель", "Категория", "Цена/ч", "Статус"]
        )
        self.clients = create_table(["ID", "ФИО", "Телефон", "E-mail", "Документ"])
        self.active = create_table(
            ["ID", "Велосипед", "Клиент", "Начало", "Плановый возврат", "Цена/ч"]
        )
        self.history = create_table(
            ["ID", "Велосипед", "Клиент", "Начало", "Возврат", "Стоимость", "Статус"]
        )

        self._build()
        self.refresh_all()

    def _buttons(self, *pairs) -> QHBoxLayout:
        layout = QHBoxLayout()
        for title, callback in pairs:
            button = QPushButton(title)
            button.clicked.connect(callback)
            layout.addWidget(button)
        layout.addStretch()
        return layout

    def _build(self) -> None:
        self._build_bikes_tab()
        self._build_clients_tab()
        self._build_rentals_tab()
        self._build_history_tab()

    def _build_bikes_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addLayout(
            self._buttons(
                ("Добавить категорию", self.add_category),
                ("Добавить велосипед", self.add_bike),
                ("Обновить", self.refresh_all),
            )
        )
        layout.addWidget(self.bikes)
        self.tabs.addTab(widget, "Велосипеды")

    def _build_clients_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addLayout(
            self._buttons(
                ("Добавить клиента", self.add_client),
                ("Обновить", self.refresh_all),
            )
        )
        layout.addWidget(self.clients)
        self.tabs.addTab(widget, "Клиенты")

    def _build_rentals_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addLayout(
            self._buttons(
                ("Оформить аренду", self.create_rental),
                ("Вернуть выбранный велосипед", self.return_selected),
                ("Обновить", self.refresh_all),
            )
        )
        layout.addWidget(QLabel("Активные аренды"))
        layout.addWidget(self.active)
        self.tabs.addTab(widget, "Аренда")

    def _build_history_tab(self) -> None:
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.addLayout(self._buttons(("Обновить историю", self.refresh_all)))
        layout.addWidget(self.history)
        self.tabs.addTab(widget, "История")

    def _handle_error(self, error: Exception) -> None:
        logger.exception("Ошибка UI: %s", error)
        if isinstance(error, BikeRentalError):
            QMessageBox.warning(self, "Ошибка", str(error))
        else:
            QMessageBox.critical(self, "Системная ошибка", str(error))

    def add_category(self) -> None:
        try:
            dialog = CategoryDialog(self)
            if dialog.exec():
                self.category_service.add_category(**dialog.get_data())
                self.refresh_all()
        except Exception as error:
            self._handle_error(error)

    def add_bike(self) -> None:
        try:
            categories = self.category_service.list_categories()
            if not categories:
                QMessageBox.information(
                    self, "Нет категорий", "Сначала добавьте категорию."
                )
                return
            dialog = BikeDialog(categories, self)
            if dialog.exec():
                self.bike_service.add_bike(**dialog.get_data())
                self.refresh_all()
        except Exception as error:
            self._handle_error(error)

    def add_client(self) -> None:
        try:
            dialog = ClientDialog(self)
            if dialog.exec():
                self.client_service.add_client(**dialog.get_data())
                self.refresh_all()
        except Exception as error:
            self._handle_error(error)

    def create_rental(self) -> None:
        try:
            bikes = self.bike_service.list_available_bikes()
            clients = self.client_service.list_clients()
            if not bikes:
                QMessageBox.information(
                    self, "Нет велосипедов", "Нет доступных велосипедов."
                )
                return
            if not clients:
                QMessageBox.information(
                    self, "Нет клиентов", "Сначала добавьте клиента."
                )
                return
            dialog = RentalDialog(bikes, clients, self)
            if dialog.exec():
                self.rental_service.create_rental(**dialog.get_data())
                self.refresh_all()
        except Exception as error:
            self._handle_error(error)

    def return_selected(self) -> None:
        try:
            row = self.active.currentRow()
            if row < 0:
                QMessageBox.information(self, "Возврат", "Выберите аренду.")
                return
            rental_id = int(self.active.item(row, 0).text())
            rental = self.rental_service.return_bike(rental_id)
            QMessageBox.information(
                self,
                "Возврат оформлен",
                f"Стоимость: {rental.total_cost} ₽",
            )
            self.refresh_all()
        except Exception as error:
            self._handle_error(error)

    def _put_row(self, table: QTableWidget, row: int, values: list[object]) -> None:
        table.insertRow(row)
        for column, value in enumerate(values):
            item = QTableWidgetItem("" if value is None else str(value))
            item.setTextAlignment(
                Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
            )
            table.setItem(row, column, item)

    def refresh_all(self) -> None:
        """Перечитать данные сервисов и обновить все таблицы окна."""
        try:
            self._refresh_bikes()
            self._refresh_clients()
            self._refresh_active_rentals()
            self._refresh_history()
        except Exception as error:
            self._handle_error(error)

    def _refresh_bikes(self) -> None:
        self.bikes.setRowCount(0)
        for row, bike in enumerate(self.bike_service.list_bikes()):
            self._put_row(
                self.bikes,
                row,
                [
                    bike.id,
                    bike.inventory_number,
                    bike.brand,
                    bike.model,
                    bike.category.name,
                    bike.category.hourly_rate,
                    "Доступен" if bike.is_available else "В аренде",
                ],
            )
        self.bikes.resizeColumnsToContents()

    def _refresh_clients(self) -> None:
        self.clients.setRowCount(0)
        for row, client in enumerate(self.client_service.list_clients()):
            self._put_row(
                self.clients,
                row,
                [
                    client.id,
                    client.full_name,
                    client.phone,
                    client.email or "",
                    client.document_number or "",
                ],
            )
        self.clients.resizeColumnsToContents()

    def _refresh_active_rentals(self) -> None:
        self.active.setRowCount(0)
        for row, rental in enumerate(self.rental_service.list_active()):
            self._put_row(
                self.active,
                row,
                [
                    rental.id,
                    rental.bike.display_name,
                    rental.client.full_name,
                    rental.started_at.strftime("%d.%m.%Y %H:%M"),
                    rental.expected_return_at.strftime("%d.%m.%Y %H:%M"),
                    rental.hourly_rate,
                ],
            )
        self.active.resizeColumnsToContents()

    def _refresh_history(self) -> None:
        self.history.setRowCount(0)
        for row, rental in enumerate(self.rental_service.list_all()):
            self._put_row(
                self.history,
                row,
                [
                    rental.id,
                    rental.bike.display_name,
                    rental.client.full_name,
                    rental.started_at.strftime("%d.%m.%Y %H:%M"),
                    (
                        rental.returned_at.strftime("%d.%m.%Y %H:%M")
                        if rental.returned_at
                        else ""
                    ),
                    rental.total_cost or "",
                    "Завершена" if rental.is_closed else "Активна",
                ],
            )
        self.history.resizeColumnsToContents()
