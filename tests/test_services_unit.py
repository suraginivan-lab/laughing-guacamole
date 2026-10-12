from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from business_logic import (
    BikeUnavailableError,
    DuplicateEntityError,
    EntityNotFoundError,
    RentalService,
    ValidationError,
)


def test_calculate_cost_less_than_hour_is_one_hour(db):
    service = RentalService(db)
    started = datetime(2026, 10, 12, 10, 0)
    returned = started + timedelta(minutes=20)

    result = service.calculate_cost(started, returned, Decimal("250.00"))

    assert result == Decimal("250.00")


def test_calculate_cost_rounds_duration_up_to_next_hour(db):
    service = RentalService(db)
    started = datetime(2026, 10, 12, 10, 0)
    returned = started + timedelta(hours=2, minutes=1)

    result = service.calculate_cost(started, returned, Decimal("250.00"))

    assert result == Decimal("750.00")


def test_calculate_cost_exact_two_hours(db):
    service = RentalService(db)
    started = datetime(2026, 10, 12, 10, 0)
    returned = started + timedelta(hours=2)

    result = service.calculate_cost(started, returned, Decimal("350.00"))

    assert result == Decimal("700.00")


def test_calculate_cost_rejects_return_before_start(db):
    service = RentalService(db)
    started = datetime(2026, 10, 12, 10, 0)

    with pytest.raises(ValidationError):
        service.calculate_cost(
            started,
            started - timedelta(minutes=1),
            Decimal("250.00"),
        )


def test_category_name_is_required(services):
    with pytest.raises(ValidationError):
        services["categories"].add_category("   ", Decimal("250.00"))


def test_category_rate_cannot_be_negative(services):
    with pytest.raises(ValidationError):
        services["categories"].add_category("Горный", Decimal("-1.00"))


def test_duplicate_category_is_rejected(services):
    services["categories"].add_category("Городской", Decimal("250.00"))

    with pytest.raises(DuplicateEntityError):
        services["categories"].add_category("Городской", Decimal("300.00"))


def test_bike_required_fields_are_validated(services, sample_data):
    category, _, _ = sample_data

    with pytest.raises(ValidationError):
        services["bikes"].add_bike("", "Stels", "Model", category.id)


def test_bike_requires_existing_category(services):
    with pytest.raises(EntityNotFoundError):
        services["bikes"].add_bike(
            "BIKE-X", "Stels", "Navigator", category_id=9999
        )


def test_duplicate_inventory_number_is_rejected(services, sample_data):
    category, bike, _ = sample_data

    with pytest.raises(DuplicateEntityError):
        services["bikes"].add_bike(
            bike.inventory_number,
            "Forward",
            "Apache",
            category.id,
        )


def test_client_full_name_is_required(services):
    with pytest.raises(ValidationError):
        services["clients"].add_client("", "+79990000001")


def test_duplicate_client_document_is_rejected(services, sample_data):
    _, _, client = sample_data

    with pytest.raises(DuplicateEntityError):
        services["clients"].add_client(
            "Петров Пётр Петрович",
            "+79990000002",
            document_number=client.document_number,
        )
