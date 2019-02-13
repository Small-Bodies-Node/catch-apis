from typing import Sequence, Any, Union, List, Type

# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy.orm.session import Session
from sqlalchemy.engine.result import ResultProxy

from models import Ztf, Test, Found


# class ZtfFound(Ztf, Found):
#     """Union class of Ztf and Found for typings"""

# ZtfFound = type('ZtfFound', (Ztf, Found), dict(a=1))


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

    def get_ztf_data(self: Any, serialize: bool = False) -> Any:
        '>>> Query DB for all ZTF data'
        all_ztf_data: Sequence[Ztf] = self.session.query(
            Ztf).order_by(Ztf.obsid).limit(50)

        x = self.session.query(Ztf)

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
        # returned_data: ResultProxy = self.session.execute(
        #     'select obsjd, ra, `dec`, dra, ddec, ra3sig, dec3sig, vmag, rh, rdot, delta, phase, selong, sangle, vangle, trueanomaly, tmtp, pid, obsdate, infobits, field, ccdid, qid, rcid, fid, filtercode, expid, filefracday, seeing, airmass, moonillf, maglimit from found inner join ztf using(obsid) where objid=909')

        all_moving_object_search_data: List[(Any)] = self.session.query(
            Found.obsjd,
            Found.ra,
            Found.dec,
            Found.dra,
            Found.ddec,
            Found.ra3sig,
            Found.dec3sig,
            Found.vmag,
            Found.rh,
            Found.rdot,
            Found.delta,
            Found.phase,
            Found.selong,
            Found.sangle,
            Found.vangle,
            Found.trueanomaly,
            Found.tmtp,
            Ztf.pid,
            Ztf.obsdate,
            Ztf.infobits,
            Ztf.field,
            Ztf.ccdid,
            Ztf.qid,
            Ztf.rcid,
            Ztf.fid,
            Ztf.filtercode,
            Ztf.expid,
            Ztf.filefracday,
            Ztf.seeing,
            Ztf.airmass,
            Ztf.moonillf,
            Ztf.maglimit
        ) \
            .join(Ztf, Found.obsid == Ztf.obsid) \
            .filter(Found.objid == objid) \
            .offset(start_row) \
            .limit(end_row - start_row)

        serialized_row: Any = {}
        all_serialized_rows: Any = []
        for row in all_moving_object_search_data:
            serialized_row = {
                "obsjd": row.obsjd,
                "ra": row.ra,
                "dec": row.dec,
                "dra": row.dra,
                "ddec": row.ddec,
                "ra3sig": row.ra3sig,
                "dec3sig": row.dec3sig,
                "vmag": row.vmag,
                "rh": row.rh,
                "rdot": row.rdot,
                "delta": row.delta,
                "phase": row.phase,
                "selong": row.selong,
                "sangle": row.sangle,
                "vangle": row.vangle,
                "trueanomaly": row.trueanomaly,
                "tmtp": row.tmtp,
                "pid": row.pid,
                "obsdate": row.obsdate,
                "infobits": row.infobits,
                "field": row.field,
                "ccdid": row.ccdid,
                "qid": row.qid,
                "rcid": row.rcid,
                "fid": row.fid,
                "filtercode": row.filtercode,
                "expid": row.expid,
                "filefracday": row.filefracday,
                "seeing": row.seeing,
                "airmass": row.airmass,
                "moonillf": row.moonillf,
                "maglimit": row.maglimit
            }
            for a in serialized_row:
                print(a)
                print(str(serialized_row[a]))
                serialized_row[a] = str(serialized_row[a])
            all_serialized_rows.append(serialized_row)

        # # [print(returned_data) for (xxx) in returned_data]
        # # self.session.query(Found)
        # for (xxx) in returned_data:
        #     print("^^^!!!")
        #     print(xxx)
        #     print(xxx.objid)
        #     print(xxx.serialize())

        print("****************")
        print(all_serialized_rows)
        print("****************")
        return all_serialized_rows


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
