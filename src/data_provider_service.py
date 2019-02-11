from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session as xxx

from typing import Sequence

from models import Ztf, Test

x1 = 'The values specified in engine'
x2 = ' parameter has to be supported by SQLAlchemy'


class DataProviderService:

    # Init engine
    def __init__(self, engine):
        if not engine:
            raise ValueError(
                x1 + x2
            )
        self.engine = engine
        db_engine = create_engine(engine)
        db_session = sessionmaker(bind=db_engine)
        self.session: xxx = db_session()
        # self.session = db_session()

    def get_ztf_data(self, serialize=False):

        # all_ztf_data = []

        all_ztf_data: Sequence[Ztf] = self.session.query(
            Ztf).order_by(Ztf.obsid).limit(50)

        # yyy: Ztf = Ztf()
        #
        yyy: Test = Test()
        print(yyy)
        # yyy.aaa
        a: int = 1.10
        b: str = "hello"
        c = b - a
        # d = a[1]
        print("c  " + c + a)

        if serialize:
            return [cand.serialize() for (cand) in all_ztf_data]
        else:
            return all_ztf_data


# Testing mypy types:
def greeting(name: str) -> str:
    return 'Hello ' + name


# Argument 1 to "greeting" has incompatible type "int"; expected "str"
# greeting(3)
# greeting(b'Alice')

# aaa: int = 1.2
# a: int = 1.10

# print(a)
