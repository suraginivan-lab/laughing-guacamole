from decimal import Decimal

import pytest

from business_logic import BikeService, CategoryService, ClientService, RentalService
from data_access import Database


@pytest.fixture()
def db():
    database = Database("sqlite:///:memory:")
    database.create_tables()
    try:
        yield database
    finally:
        database.engine.dispose()


@pytest.fixture()
def services(db):
    return {
        "categories": CategoryService(db),
        "bikes": BikeService(db),
        "clients": ClientService(db),
        "rentals": RentalService(db),
    }


@pytest.fixture()
def sample_data(services):
    category = services["categories"].add_category(
        "Городской", Decimal("250.00"), "Для городской езды"
    )
    bike = services["bikes"].add_bike(
        "BIKE-TEST-001", "Stels", "Navigator", category.id
    )
    client = services["clients"].add_client(
        "Иванов Иван Иванович",
        "+79990000001",
        "ivanov@example.com",
        "4510 123456",
    )
    return category, bike, client
