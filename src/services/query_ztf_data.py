'''Query DB for ZTF data'''

from typing import Any, List, Dict
from decimal import Decimal
from models.models import Ztf, Found
from .database_provider import DATA_PROVIDER_SESSION


def query_ztf_found_data(start_row: int = 0, end_row: int = -1, objid: int = -1) -> Any:
    '''Query DB for ZTF found data'''
    found_ztf_data: List[Any]

    found_ztf_data = (
        DATA_PROVIDER_SESSION
        .query(
            Found.foundid,
            Found.objid,
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
        )
        .join(Ztf, Found.obsid == Ztf.obsid)
    )

    if objid > 0:
        found_ztf_data = found_ztf_data.filter(Found.objid == objid)

    found_ztf_data = (
        found_ztf_data
        .offset(start_row)
        .limit(500 if end_row == -1 else end_row - start_row)
    )

    serialized_row: Dict[Any] = {}
    all_serialized_rows: List[dict] = []
    for row in found_ztf_data:
        serialized_row = {
            "foundid": row.foundid,
            "objid": row.objid,
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
