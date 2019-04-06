'''Query DB for ZTF data'''

from typing import Any, Sequence
# from models.models import t_ztf_found as ZtfFound
from models.models import Ztf, Found
from .database_provider import DATA_PROVIDER_SESSION


def query_ztf_found_data(start_row: int = 0, end_row: int = -1, objid: int = -1) -> Any:
    '''Query DB for ZTF found data'''
    found_ztf_data: Any  # Sequence[ZtfFound]

    found_ztf_data = (DATA_PROVIDER_SESSION
                      .query(Found)
                      .join(Ztf, Found.obsid == Ztf.obsid))

    if objid > 0:
        (found_ztf_data
         .filter(Found.objid == objid)
         .order_by(Found.foundid))

    if end_row == -1:
        found_ztf_data.limit(500)
    else:
        found_ztf_data.offset(start_row).limit(end_row - start_row)

    return [ztf_row.serialize() for (ztf_row) in found_ztf_data]
