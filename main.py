import logging,sys
from pathlib import Path
from PySide6.QtWidgets import QApplication
from business_logic import BikeService,CategoryService,ClientService,RentalService
from data_access import Database
from logging_config import configure_logging
from presentation import MainWindow
from seed import seed_demo_data

def main():
    configure_logging(); logging.getLogger(__name__).info('Запуск приложения')
    path=Path(__file__).resolve().parent/'bike_rental.db'; db=Database(f'sqlite:///{path.as_posix()}'); db.create_tables(); seed_demo_data(db)
    app=QApplication(sys.argv); w=MainWindow(CategoryService(db),BikeService(db),ClientService(db),RentalService(db)); w.show(); return app.exec()
if __name__=='__main__': raise SystemExit(main())
