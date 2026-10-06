import logging
from PySide6.QtWidgets import QAbstractItemView,QHBoxLayout,QLabel,QMainWindow,QMessageBox,QPushButton,QStatusBar,QTabWidget,QTableWidget,QTableWidgetItem,QVBoxLayout,QWidget
from business_logic import BikeRentalError
from .dialogs import BikeDialog,CategoryDialog,ClientDialog,RentalDialog
logger=logging.getLogger(__name__)

def table(headers):
    t=QTableWidget(0,len(headers)); t.setHorizontalHeaderLabels(headers); t.setSelectionBehavior(QAbstractItemView.SelectRows); t.setSelectionMode(QAbstractItemView.SingleSelection); t.setEditTriggers(QAbstractItemView.NoEditTriggers); t.horizontalHeader().setStretchLastSection(True); return t

class MainWindow(QMainWindow):
    def __init__(self,category_service,bike_service,client_service,rental_service):
        super().__init__(); self.category_service=category_service; self.bike_service=bike_service; self.client_service=client_service; self.rental_service=rental_service
        self.setWindowTitle('Прокат велосипедов'); self.resize(1050,650); self.setStatusBar(QStatusBar()); self.tabs=QTabWidget(); self.setCentralWidget(self.tabs)
        self.bikes=table(['ID','Инв. №','Марка','Модель','Категория','Цена/ч','Статус']); self.clients=table(['ID','ФИО','Телефон','E-mail','Документ']); self.active=table(['ID','Велосипед','Клиент','Начало','Плановый возврат','Цена/ч']); self.history=table(['ID','Велосипед','Клиент','Начало','Возврат','Стоимость','Статус'])
        self._build(); self.refresh_all()
    def _buttons(self,*pairs):
        l=QHBoxLayout()
        for title,fn in pairs:
            b=QPushButton(title); b.clicked.connect(fn); l.addWidget(b)
        l.addStretch(); return l
    def _build(self):
        w=QWidget(); l=QVBoxLayout(w); l.addLayout(self._buttons(('Добавить категорию',self.add_category),('Добавить велосипед',self.add_bike),('Обновить',self.refresh_all))); l.addWidget(self.bikes); self.tabs.addTab(w,'Велосипеды')
        w=QWidget(); l=QVBoxLayout(w); l.addLayout(self._buttons(('Добавить клиента',self.add_client),('Обновить',self.refresh_all))); l.addWidget(self.clients); self.tabs.addTab(w,'Клиенты')
        w=QWidget(); l=QVBoxLayout(w); l.addLayout(self._buttons(('Оформить аренду',self.create_rental),('Вернуть выбранный велосипед',self.return_selected),('Обновить',self.refresh_all))); l.addWidget(QLabel('Активные аренды')); l.addWidget(self.active); self.tabs.addTab(w,'Аренда')
        w=QWidget(); l=QVBoxLayout(w); l.addLayout(self._buttons(('Обновить историю',self.refresh_all))); l.addWidget(self.history); self.tabs.addTab(w,'История')
    def err(self,e):
        logger.exception('Ошибка UI: %s',e)
        (QMessageBox.warning if isinstance(e,BikeRentalError) else QMessageBox.critical)(self,'Ошибка',str(e))
    def add_category(self):
        try:
            d=CategoryDialog(self)
            if d.exec(): self.category_service.add_category(**d.get_data()); self.refresh_all()
        except Exception as e: self.err(e)
    def add_bike(self):
        try:
            cats=self.category_service.list_categories()
            if not cats: QMessageBox.information(self,'Нет категорий','Сначала добавьте категорию.'); return
            d=BikeDialog(cats,self)
            if d.exec(): self.bike_service.add_bike(**d.get_data()); self.refresh_all()
        except Exception as e: self.err(e)
    def add_client(self):
        try:
            d=ClientDialog(self)
            if d.exec(): self.client_service.add_client(**d.get_data()); self.refresh_all()
        except Exception as e: self.err(e)
    def create_rental(self):
        try:
            bikes=self.bike_service.list_available_bikes(); clients=self.client_service.list_clients()
            if not bikes: QMessageBox.information(self,'Нет велосипедов','Нет доступных велосипедов.'); return
            if not clients: QMessageBox.information(self,'Нет клиентов','Сначала добавьте клиента.'); return
            d=RentalDialog(bikes,clients,self)
            if d.exec(): self.rental_service.create_rental(**d.get_data()); self.refresh_all()
        except Exception as e: self.err(e)
    def return_selected(self):
        try:
            row=self.active.currentRow()
            if row<0: QMessageBox.information(self,'Возврат','Выберите аренду.'); return
            rid=int(self.active.item(row,0).text()); x=self.rental_service.return_bike(rid); QMessageBox.information(self,'Возврат оформлен',f'Стоимость: {x.total_cost} ₽'); self.refresh_all()
        except Exception as e: self.err(e)
    def put(self,t,row,vals):
        t.insertRow(row)
        for c,v in enumerate(vals): t.setItem(row,c,QTableWidgetItem('' if v is None else str(v)))
    def refresh_all(self):
        try:
            self.bikes.setRowCount(0)
            for r,b in enumerate(self.bike_service.list_bikes()): self.put(self.bikes,r,[b.id,b.inventory_number,b.brand,b.model,b.category.name,b.category.hourly_rate,'Доступен' if b.is_available else 'В аренде'])
            self.clients.setRowCount(0)
            for r,c in enumerate(self.client_service.list_clients()): self.put(self.clients,r,[c.id,c.full_name,c.phone,c.email or '',c.document_number or ''])
            self.active.setRowCount(0)
            for r,x in enumerate(self.rental_service.list_active()): self.put(self.active,r,[x.id,x.bike.display_name,x.client.full_name,x.started_at.strftime('%d.%m.%Y %H:%M'),x.expected_return_at.strftime('%d.%m.%Y %H:%M'),x.hourly_rate])
            self.history.setRowCount(0)
            for r,x in enumerate(self.rental_service.list_all()): self.put(self.history,r,[x.id,x.bike.display_name,x.client.full_name,x.started_at.strftime('%d.%m.%Y %H:%M'),x.returned_at.strftime('%d.%m.%Y %H:%M') if x.returned_at else '',x.total_cost or '','Завершена' if x.is_closed else 'Активна'])
            for t in (self.bikes,self.clients,self.active,self.history): t.resizeColumnsToContents()
        except Exception as e: self.err(e)
