from decimal import Decimal
from business_logic import BikeService,CategoryService,ClientService

def seed_demo_data(db):
    cs,bs,cls=CategoryService(db),BikeService(db),ClientService(db)
    if not cs.list_categories():
        city=cs.add_category('Городской',Decimal('250'),'Для городской езды'); mountain=cs.add_category('Горный',Decimal('350'),'Для пересечённой местности')
        bs.add_bike('BIKE-001','Stels','Navigator 500',city.id); bs.add_bike('BIKE-002','Forward','Apache 27.5',mountain.id); bs.add_bike('BIKE-003','Giant','Escape 3',city.id)
    if not cls.list_clients():
        cls.add_client('Иванов Иван Иванович','+79990000001','ivanov@example.com','4510 123456'); cls.add_client('Петрова Анна Сергеевна','+79990000002','petrova@example.com','4511 654321')
