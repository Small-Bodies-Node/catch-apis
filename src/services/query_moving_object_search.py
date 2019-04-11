'''
Function to query SQL DB for moving-object-search
'''


from typing import List, Any
from decimal import Decimal
from models.models import Ztf, Found
from .database_provider import DATA_PROVIDER_SESSION


def query_moving_object_search(
    objid: str,
    start_row: int = 0,
    end_row: int = 10
) -> Any:
    ''' Join query for moving object search'''
    with DATA_PROVIDER_SESSION() as session:
        all_moving_object_search_data: List[(Any)] = session.query(
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
            # Convert items in binary row to tpython data structures
            for a in serialized_row:
                if isinstance(serialized_row[a], Decimal):
                    serialized_row[a] = float(serialized_row[a])
                elif isinstance(serialized_row[a], int):
                    serialized_row[a] = int(serialized_row[a])
                else:
                    serialized_row[a] = str(serialized_row[a])
            all_serialized_rows.append(serialized_row)

    return all_serialized_rows
