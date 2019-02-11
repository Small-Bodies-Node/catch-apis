from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session as xxx

from typing import Sequence, Any

from models import Ztf, Test

x1: str = 'The values specified in engine'
x2: str = ' parameter has to be supported by SQLAlchemy'


class DataProviderService:

    # Init engine
    def __init__(self: Any, engine_uri: str) -> None:
        if not engine_uri:
            raise ValueError(
                x1 + x2
            )
        self.engine_uri = engine_uri
        db_engine = create_engine(engine_uri)
        db_session = sessionmaker(bind=db_engine)
        self.session: xxx = db_session()
        # self.session = db_session()

    def get_ztf_data(self, serialize=False):

        all_ztf_data: Sequence[Ztf] = self.session.query(
            Ztf).order_by(Ztf.obsid).limit(50)

        if serialize:
            return [cand.serialize() for (cand) in all_ztf_data]
        else:
            return all_ztf_data

    def get_moving_object_search_data(
        self: Any,
        objid: str,
        start_row: int = 0,
        end_row: int = 10
    ) -> Any:
        # a: int = 1.2
        print(str(start_row) + " " + str(end_row))
        # returned_data: Any = self.session.query(
        #     Ztf).order_by(Ztf.obsid).limit(50)
        returned_data: Any = self.session.execute(
            ''
        )
        print("****************")
        print(returned_data)
        print("****************")
        return returned_data


def greeting(name: str) -> str:
    return 'Hello ' + name


# Argument 1 to "greeting" has incompatible type "int"; expected "str"
# greeting(3)
# greeting(b'Alice')

# aaa: int = 1.2
# a: int = 1.10

# b: str = "hello"
# c = b * b
# print(a)


# class TestClass:
#     def __init__(self, engine):
#         print('yyy')

#     def blah(self):
#         print('xxx')
#         aaa: int = 1.2
