from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from business_logic import (
    BikeUnavailableError,
    EntityNotFoundError,
    RentalAlreadyClosedError,
    ValidationError,
)
from data_access.repositories import BikeRepository, RentalRepository


def test_create_rental_persists_rental_and_marks_bike_unavailable(
    db, services, sample_data
):
    _, bike, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)

    rental = services["rentals"].create_rental(
        bike.id,
        client.id,
        started + timedelta(hours=2),
        started_at=started,
    )

    with db.session_scope() as session:
        saved_rental = RentalRepository(session).get_by_id(rental.id)
        saved_bike = BikeRepository(session).get_by_id(bike.id)

        assert saved_rental is not None
        assert saved_rental.bike_id == bike.id
        assert saved_rental.client_id == client.id
        assert saved_rental.is_closed is False
        assert saved_bike.is_available is False


def test_active_rental_appears_in_active_list(services, sample_data):
    _, bike, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)

    created = services["rentals"].create_rental(
        bike.id,
        client.id,
        started + timedelta(hours=1),
        started_at=started,
    )

    active = services["rentals"].list_active()

    assert [r.id for r in active] == [created.id]


def test_same_bike_cannot_be_rented_twice(services, sample_data):
    _, bike, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)

    services["rentals"].create_rental(
        bike.id,
        client.id,
        started + timedelta(hours=1),
        started_at=started,
    )

    with pytest.raises(BikeUnavailableError):
        services["rentals"].create_rental(
            bike.id,
            client.id,
            started + timedelta(hours=3),
            started_at=started + timedelta(minutes=5),
        )


def test_rental_requires_existing_bike(services, sample_data):
    _, _, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)

    with pytest.raises(EntityNotFoundError):
        services["rentals"].create_rental(
            9999,
            client.id,
            started + timedelta(hours=1),
            started_at=started,
        )


def test_expected_return_must_be_after_start(services, sample_data):
    _, bike, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)

    with pytest.raises(ValidationError):
        services["rentals"].create_rental(
            bike.id,
            client.id,
            started,
            started_at=started,
        )


def test_return_bike_closes_rental_calculates_cost_and_releases_bike(
    db, services, sample_data
):
    _, bike, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)
    rental = services["rentals"].create_rental(
        bike.id,
        client.id,
        started + timedelta(hours=3),
        started_at=started,
    )

    returned = services["rentals"].return_bike(
        rental.id,
        returned_at=started + timedelta(hours=2, minutes=10),
    )

    assert returned.is_closed is True
    assert returned.total_cost == Decimal("750.00")

    with db.session_scope() as session:
        saved_bike = BikeRepository(session).get_by_id(bike.id)
        saved_rental = RentalRepository(session).get_by_id(rental.id)
        assert saved_bike.is_available is True
        assert saved_rental.is_closed is True
        assert saved_rental.total_cost == Decimal("750.00")


def test_closed_rental_is_removed_from_active_list(services, sample_data):
    _, bike, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)
    rental = services["rentals"].create_rental(
        bike.id,
        client.id,
        started + timedelta(hours=2),
        started_at=started,
    )
    services["rentals"].return_bike(
        rental.id,
        returned_at=started + timedelta(hours=1),
    )

    assert services["rentals"].list_active() == []
    assert any(r.id == rental.id for r in services["rentals"].list_all())


def test_rental_cannot_be_closed_twice(services, sample_data):
    _, bike, client = sample_data
    started = datetime(2026, 10, 12, 10, 0)
    rental = services["rentals"].create_rental(
        bike.id,
        client.id,
        started + timedelta(hours=2),
        started_at=started,
    )
    services["rentals"].return_bike(
        rental.id,
        returned_at=started + timedelta(hours=1),
    )

    with pytest.raises(RentalAlreadyClosedError):
        services["rentals"].return_bike(
            rental.id,
            returned_at=started + timedelta(hours=2),
        )
