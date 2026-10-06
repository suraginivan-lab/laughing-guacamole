from contextlib import contextmanager
from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

class Base(DeclarativeBase):
    pass

class Database:
    def __init__(self, url='sqlite:///bike_rental.db', echo=False):
        args = {'check_same_thread': False} if url.startswith('sqlite') else {}
        self.engine = create_engine(url, echo=echo, future=True, connect_args=args)
        if url.startswith('sqlite'):
            @event.listens_for(self.engine, 'connect')
            def _fk_on(conn, _):
                cur = conn.cursor(); cur.execute('PRAGMA foreign_keys=ON'); cur.close()
        self._factory = sessionmaker(bind=self.engine, class_=Session, autoflush=False, expire_on_commit=False)

    def create_tables(self):
        from . import models  # noqa
        Base.metadata.create_all(self.engine)

    def session(self):
        return self._factory()

    @contextmanager
    def session_scope(self):
        s = self.session()
        try:
            yield s
            s.commit()
        except Exception:
            s.rollback()
            raise
        finally:
            s.close()
