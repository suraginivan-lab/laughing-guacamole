from decimal import Decimal, InvalidOperation
from PySide6.QtCore import QDateTime
from PySide6.QtWidgets import QComboBox,QDateTimeEdit,QDialog,QDialogButtonBox,QFormLayout,QLineEdit,QTextEdit,QVBoxLayout
from business_logic import ValidationError

class BaseDialog(QDialog):
    def buttons(self, layout):
        b=QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel); b.accepted.connect(self.accept); b.rejected.connect(self.reject); layout.addWidget(b)

class CategoryDialog(BaseDialog):
    def __init__(self,p=None):
        super().__init__(p); self.setWindowTitle('Новая категория'); self.name=QLineEdit(); self.rate=QLineEdit(); self.desc=QTextEdit(); f=QFormLayout(); f.addRow('Название:',self.name); f.addRow('Цена за час:',self.rate); f.addRow('Описание:',self.desc); l=QVBoxLayout(self); l.addLayout(f); self.buttons(l)
    def get_data(self):
        try: rate=Decimal(self.rate.text().replace(',','.'))
        except InvalidOperation as e: raise ValidationError('Введите корректную стоимость.') from e
        return dict(name=self.name.text(),hourly_rate=rate,description=self.desc.toPlainText())

class BikeDialog(BaseDialog):
    def __init__(self,categories,p=None):
        super().__init__(p); self.setWindowTitle('Новый велосипед'); self.inv=QLineEdit(); self.brand=QLineEdit(); self.model=QLineEdit(); self.cat=QComboBox(); self.notes=QLineEdit()
        for c in categories: self.cat.addItem(f'{c.name} ({c.hourly_rate} ₽/ч)',c.id)
        f=QFormLayout(); [f.addRow(a,b) for a,b in [('Инвентарный №:',self.inv),('Марка:',self.brand),('Модель:',self.model),('Категория:',self.cat),('Примечание:',self.notes)]]; l=QVBoxLayout(self); l.addLayout(f); self.buttons(l)
    def get_data(self): return dict(inventory_number=self.inv.text(),brand=self.brand.text(),model=self.model.text(),category_id=int(self.cat.currentData()),notes=self.notes.text())

class ClientDialog(BaseDialog):
    def __init__(self,p=None):
        super().__init__(p); self.setWindowTitle('Новый клиент'); self.name=QLineEdit(); self.phone=QLineEdit(); self.email=QLineEdit(); self.doc=QLineEdit(); f=QFormLayout(); [f.addRow(a,b) for a,b in [('ФИО:',self.name),('Телефон:',self.phone),('E-mail:',self.email),('Документ:',self.doc)]]; l=QVBoxLayout(self); l.addLayout(f); self.buttons(l)
    def get_data(self): return dict(full_name=self.name.text(),phone=self.phone.text(),email=self.email.text(),document_number=self.doc.text())

class RentalDialog(BaseDialog):
    def __init__(self,bikes,clients,p=None):
        super().__init__(p); self.setWindowTitle('Оформление аренды'); self.bike=QComboBox(); self.client=QComboBox(); self.ret=QDateTimeEdit(); self.ret.setCalendarPopup(True); self.ret.setDateTime(QDateTime.currentDateTime().addSecs(7200))
        for b in bikes: self.bike.addItem(b.display_name,b.id)
        for c in clients: self.client.addItem(f'{c.full_name} — {c.phone}',c.id)
        f=QFormLayout(); f.addRow('Велосипед:',self.bike); f.addRow('Клиент:',self.client); f.addRow('Плановый возврат:',self.ret); l=QVBoxLayout(self); l.addLayout(f); self.buttons(l)
    def get_data(self): return dict(bike_id=int(self.bike.currentData()),client_id=int(self.client.currentData()),expected_return_at=self.ret.dateTime().toPython())
