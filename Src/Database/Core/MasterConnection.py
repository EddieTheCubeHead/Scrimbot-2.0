__version__ = "0.1"
__author__ = "Eetu Asikainen"

import sqlalchemy
import sqlalchemy.orm


class MasterConnection:

    def __init__(self, db_address: str):
        self.engine = sqlalchemy.create_engine(f"sqlite:///{db_address}", echo=True)
        self.session = sqlalchemy.orm.sessionmaker()
        self.session.configure(bind=self.engine)

    def get_session(self):
        return self.session()
