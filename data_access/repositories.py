from sqlalchemy import select
from sqlalchemy.orm import joinedload
from .models import Bike, BikeCategory, Client, Rental

class BaseRepository:
    model = None
    def __init__(self, session): self.session = session
    def get_by_id(self, entity_id): return self.session.get(self.model, entity_id)
    def get_all(self): return list(self.session.scalars(select(self.model)).all())
    def add(self, entity): self.session.add(entity); self.session.flush(); return entity
    def update(self, entity): entity = self.session.merge(entity); self.session.flush(); return entity
    def delete(self, entity): self.session.delete(entity); self.session.flush()

class BikeCategoryRepository(BaseRepository):
    model = BikeCategory
    def get_all(self): return list(self.session.scalars(select(BikeCategory).order_by(BikeCategory.name)).all())
    def get_by_name(self, name): return self.session.scalar(select(BikeCategory).where(BikeCategory.name == name))

class BikeRepository(BaseRepository):
    model = Bike
    def get_all(self):
        q = select(Bike).options(joinedload(Bike.category)).order_by(Bike.id)
        return list(self.session.scalars(q).all())
    def get_available(self):
        q = select(Bike).options(joinedload(Bike.category)).where(Bike.is_available.is_(True)).order_by(Bike.id)
        return list(self.session.scalars(q).all())
    def get_by_inventory_number(self, value): return self.session.scalar(select(Bike).where(Bike.inventory_number == value))

class ClientRepository(BaseRepository):
    model = Client
    def get_all(self): return list(self.session.scalars(select(Client).order_by(Client.full_name)).all())
    def get_by_document_number(self, value): return self.session.scalar(select(Client).where(Client.document_number == value))

class RentalRepository(BaseRepository):
    model = Rental
    def _base(self): return select(Rental).options(joinedload(Rental.bike).joinedload(Bike.category), joinedload(Rental.client))
    def get_all(self): return list(self.session.scalars(self._base().order_by(Rental.started_at.desc())).all())
    def get_active(self): return list(self.session.scalars(self._base().where(Rental.is_closed.is_(False)).order_by(Rental.started_at.desc())).all())
    def get_active_for_bike(self, bike_id):
        return self.session.scalar(select(Rental).where(Rental.bike_id == bike_id, Rental.is_closed.is_(False)))
