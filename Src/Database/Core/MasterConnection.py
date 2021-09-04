__version__ = "0.1"
__author__ = "Eetu Asikainen"

from contextlib import contextmanager
from typing import ContextManager

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from Bot.DataClasses.Convertable import Convertable


class MasterConnection:

    def __init__(self, db_address: str, debug=False):
        self.engine = sqlalchemy.create_engine(f"sqlite:///{db_address}", echo=debug)
        self.session = sqlalchemy.orm.sessionmaker()
        self.session.configure(bind=self.engine)
        Convertable.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> ContextManager[Session]:
        session = self.session()
        try:
            yield session
            session.commit()
        except SQLAlchemyError:  # pragma: no cover
            session.rollback()
            raise  # TODO inspect error handling here: this is not good, also remove the no cover
        finally:
            session.close()
