from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class BikeCategory(Base):
    __tablename__ = 'bike_categories'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    bikes: Mapped[list['Bike']] = relationship(back_populates='category')
    __table_args__ = (CheckConstraint('hourly_rate >= 0'),)

class Bike(Base):
    __tablename__ = 'bikes'
    id: Mapped[int] = mapped_column(primary_key=True)
    inventory_number: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    brand: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey('bike_categories.id', ondelete='RESTRICT'), nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(Text)
    category: Mapped['BikeCategory'] = relationship(back_populates='bikes')
    rentals: Mapped[list['Rental']] = relationship(back_populates='bike')
    @property
    def display_name(self): return f'{self.inventory_number} — {self.brand} {self.model}'

class Client(Base):
    __tablename__ = 'clients'
    id: Mapped[int] = mapped_column(primary_key=True)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    phone: Mapped[str] = mapped_column(String(30), nullable=False, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(150))
    document_number: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    rentals: Mapped[list['Rental']] = relationship(back_populates='client')

class Rental(Base):
    __tablename__ = 'rentals'
    id: Mapped[int] = mapped_column(primary_key=True)
    bike_id: Mapped[int] = mapped_column(ForeignKey('bikes.id', ondelete='RESTRICT'), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey('clients.id', ondelete='RESTRICT'), nullable=False, index=True)
    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    expected_return_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    returned_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    hourly_rate: Mapped[Decimal] = mapped_column(Numeric(10,2), nullable=False)
    total_cost: Mapped[Optional[Decimal]] = mapped_column(Numeric(10,2))
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    bike: Mapped['Bike'] = relationship(back_populates='rentals')
    client: Mapped['Client'] = relationship(back_populates='rentals')
    __table_args__ = (
        CheckConstraint('hourly_rate >= 0'),
        CheckConstraint('total_cost IS NULL OR total_cost >= 0'),
        CheckConstraint('expected_return_at > started_at'),
    )
