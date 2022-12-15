__version__ = "0.1"
__author__ = "Eetu Asikainen"

from contextlib import contextmanager
from typing import ContextManager

import sqlalchemy
import sqlalchemy.orm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from hintedi import HinteDI

from Src.Bot.DataClasses.DataClass import DataClass
from Configs.Config import Config


@HinteDI.singleton
class MasterConnection:

    @HinteDI.inject
    def __init__(self, config: Config, db_address: str = None, debug=False):
        db_address = db_address or f"{config.file_folder}/{config.database_name}"
        self.engine = sqlalchemy.create_engine(f"sqlite:///{db_address}", echo=debug)
        self.session = sqlalchemy.orm.sessionmaker()
        self.session.configure(bind=self.engine)
        DataClass.metadata.create_all(self.engine)

    @contextmanager
    def get_session(self) -> ContextManager[Session]:
        session = self.session()
        try:
            session.expire_on_commit = False
            yield session
        except SQLAlchemyError:  # pragma: no cover
            session.rollback()
            raise  # TODO inspect error handling here: this is not good, also remove the no cover
        else:
            session.commit()
        finally:
            session.close()
