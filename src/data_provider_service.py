from typing import Sequence, Any

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.orm.session import Session
from sqlalchemy.engine.result import ResultProxy

from models import Ztf, Test


class DataProviderService:
    '>>> Service Class for Querying DB'

    def __init__(self: Any, engine_uri: str) -> None:
        if not engine_uri:
            raise ValueError(
                '''
                The values specified in engine
                parameter has to be supported by SQLAlchemy
                '''
            )
        self.engine_uri = engine_uri
        db_engine = sqlalchemy.create_engine(engine_uri)
        db_session = sqlalchemy.orm.sessionmaker(bind=db_engine)
        self.session: Session = db_session()
        # self.session = db_session()

    def get_ztf_data(self, serialize=False):
        '>>> Query DB for all ZTF data'
        all_ztf_data: Sequence[Ztf] = self.session.query(
            Ztf).order_by(Ztf.obsid).limit(50)

        if serialize:
            return [ztf_row.serialize() for (ztf_row) in all_ztf_data]
        else:
            return all_ztf_data

    def get_moving_object_search_data(
        self: Any,
        objid: str,
        start_row: int = 0,
        end_row: int = 10
    ) -> Any:
        '>>> Query DB for moving-object-search'
        print(str(start_row) + " " + str(end_row))
        # returned_data: Any = self.session.query(
        #     Ztf).order_by(Ztf.obsid).limit(50)
        returned_data: ResultProxy = self.session.execute(
            "users = Table('users', metadata, Column('id', Integer, primary_key=True),     Column('name', String),   Column('fullname', String)  )"
        )
        print("****************")
        print(returned_data.fetchall())
        print("****************")
        return returned_data


def greeting(name: str) -> str:
    '>>> Test Doc String'
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
