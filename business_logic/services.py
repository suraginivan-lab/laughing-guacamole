import logging, math
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from data_access import Bike, BikeCategory, Client, Rental
from data_access.repositories import BikeCategoryRepository, BikeRepository, ClientRepository, RentalRepository
from .exceptions import *
from .interfaces import IRentalService

logger = logging.getLogger(__name__)

def req(value, title):
    value = value.strip()
    if not value: raise ValidationError(f'Поле «{title}» обязательно.')
    return value

class CategoryService:
    def __init__(self, db): self.db = db
    def list_categories(self):
        with self.db.session_scope() as s: return BikeCategoryRepository(s).get_all()
    def add_category(self, name, hourly_rate, description=None):
        name = req(name, 'Название категории')
        if hourly_rate < 0: raise ValidationError('Стоимость не может быть отрицательной.')
        with self.db.session_scope() as s:
            r = BikeCategoryRepository(s)
            if r.get_by_name(name): raise DuplicateEntityError('Такая категория уже существует.')
            x = BikeCategory(name=name, hourly_rate=hourly_rate, description=(description or '').strip() or None)
            r.add(x); logger.info('Категория создана: %s', name); return x

class BikeService:
    def __init__(self, db): self.db = db
    def list_bikes(self):
        with self.db.session_scope() as s: return BikeRepository(s).get_all()
    def list_available_bikes(self):
        with self.db.session_scope() as s: return BikeRepository(s).get_available()
    def add_bike(self, inventory_number, brand, model, category_id, notes=None):
        inventory_number, brand, model = req(inventory_number,'Инвентарный номер'), req(brand,'Марка'), req(model,'Модель')
        with self.db.session_scope() as s:
            br, cr = BikeRepository(s), BikeCategoryRepository(s)
            if br.get_by_inventory_number(inventory_number): raise DuplicateEntityError('Такой инвентарный номер уже существует.')
            if not cr.get_by_id(category_id): raise EntityNotFoundError('Категория не найдена.')
            x = Bike(inventory_number=inventory_number, brand=brand, model=model, category_id=category_id, notes=(notes or '').strip() or None, is_available=True)
            br.add(x); logger.info('Велосипед добавлен: %s', inventory_number); return x

class ClientService:
    def __init__(self, db): self.db = db
    def list_clients(self):
        with self.db.session_scope() as s: return ClientRepository(s).get_all()
    def add_client(self, full_name, phone, email=None, document_number=None):
        full_name, phone = req(full_name,'ФИО'), req(phone,'Телефон')
        document_number = (document_number or '').strip() or None
        with self.db.session_scope() as s:
            r = ClientRepository(s)
            if document_number and r.get_by_document_number(document_number): raise DuplicateEntityError('Клиент с таким документом уже существует.')
            x = Client(full_name=full_name, phone=phone, email=(email or '').strip() or None, document_number=document_number)
            r.add(x); logger.info('Клиент добавлен: %s', full_name); return x

class RentalService(IRentalService):
    def __init__(self, db): self.db = db
    def list_all(self):
        with self.db.session_scope() as s: return RentalRepository(s).get_all()
    def list_active(self):
        with self.db.session_scope() as s: return RentalRepository(s).get_active()
    def create_rental(self, bike_id, client_id, expected_return_at, started_at=None):
        started_at = started_at or datetime.now()
        if expected_return_at <= started_at: raise ValidationError('Плановый возврат должен быть позже начала аренды.')
        with self.db.session_scope() as s:
            br, cr, rr, catr = BikeRepository(s), ClientRepository(s), RentalRepository(s), BikeCategoryRepository(s)
            bike, client = br.get_by_id(bike_id), cr.get_by_id(client_id)
            if not bike: raise EntityNotFoundError('Велосипед не найден.')
            if not client: raise EntityNotFoundError('Клиент не найден.')
            if not bike.is_available or rr.get_active_for_bike(bike_id): raise BikeUnavailableError('Этот велосипед уже находится в аренде.')
            cat = catr.get_by_id(bike.category_id)
            x = Rental(bike_id=bike.id, client_id=client.id, started_at=started_at, expected_return_at=expected_return_at, hourly_rate=cat.hourly_rate, is_closed=False)
            rr.add(x); bike.is_available=False; br.update(bike)
            logger.info('Аренда создана id=%s bike=%s client=%s', x.id, bike.inventory_number, client.full_name)
            return x
    def return_bike(self, rental_id, returned_at=None):
        returned_at = returned_at or datetime.now()
        with self.db.session_scope() as s:
            rr, br = RentalRepository(s), BikeRepository(s)
            x = rr.get_by_id(rental_id)
            if not x: raise EntityNotFoundError('Аренда не найдена.')
            if x.is_closed: raise RentalAlreadyClosedError('Эта аренда уже завершена.')
            if returned_at < x.started_at: raise ValidationError('Время возврата не может быть раньше начала аренды.')
            x.returned_at=returned_at; x.total_cost=self.calculate_cost(x.started_at, returned_at, x.hourly_rate); x.is_closed=True; rr.update(x)
            bike = br.get_by_id(x.bike_id)
            if not bike: raise EntityNotFoundError('Связанный велосипед не найден.')
            bike.is_available=True; br.update(bike)
            logger.info('Возврат аренды id=%s стоимость=%s', x.id, x.total_cost); return x
    def calculate_cost(self, started_at, returned_at, hourly_rate):
        seconds=(returned_at-started_at).total_seconds()
        if seconds < 0: raise ValidationError('Некорректный временной интервал.')
        hours=max(1, math.ceil(seconds/3600))
        return (Decimal(hours)*Decimal(hourly_rate)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
