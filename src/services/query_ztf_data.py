'''Query DB for ZTF data'''

import os
from typing import Any, List, Dict
from decimal import Decimal
import sqlalchemy as sa
from models.models import Ztf, Found, Obj, ZtfCutout, ZtfNight
from .database_provider import DATA_PROVIDER_SESSION


def query_ztf_found_objects() -> Any:
    """Return ZTF found object list."""

    objects: Any

    with DATA_PROVIDER_SESSION() as session:
        objects = (
            session
            .query(
                Found.objid,
                Obj.desg,
                sa.func.min(Found.obsjd),
                sa.func.max(Found.obsjd)
            )
            .join(Obj, Obj.objid == Found.objid)
            .group_by(Found.objid)
            .order_by(Obj.desg + 0, Obj.desg)
        )

        serialized_row: Dict[str, Any] = {}
        all_serialized_rows: List[dict] = []
        for row in objects:
            print(row)
            serialized_row = {
                "objid": row.objid,
                "desg": row.desg,
                "obsjd_min": row[2],
                "obsjd_max": row[3]
            }

            for key, val in serialized_row.items():
                if isinstance(val, Decimal):
                    serialized_row[key] = float(val)
                elif isinstance(val, int):
                    serialized_row[key] = int(val)
                else:
                    serialized_row[key] = str(val)
            all_serialized_rows.append(serialized_row)

    return all_serialized_rows


def query_ztf_found_data(start_row: int = 0, end_row: int = -1,
                         objid: int = -1, nightid: int = -1,
                         maglimit: float = 0, seeing: float = 0) -> Any:
    '''Query DB for ZTF found data.'''
    found_ztf_data: Any

    with DATA_PROVIDER_SESSION() as session:
        found_ztf_data = (
            session
            .query(
                Found,
                Ztf,
                ZtfCutout,
                sa.func.substr(sa.cast(Ztf.filefracday, sa.String), 1, 4)
                .label('year'),
                sa.func.substr(sa.cast(Ztf.filefracday, sa.String), 5, 4)
                .label('monthday'),
                sa.func.substr(sa.cast(Ztf.filefracday, sa.String), 9)
                .label('fracday')
            )
            .join(Ztf, Found.obsid == Ztf.obsid)
            # the cutout may not exist, use left outer join:
            .outerjoin(ZtfCutout, Found.foundid == ZtfCutout.foundid)
        )

        if maglimit > 0:
            found_ztf_data = found_ztf_data.filter(Ztf.maglimit > maglimit)

        if nightid > 0:
            found_ztf_data = found_ztf_data.filter(Ztf.nightid == nightid)

        if seeing > 0:
            found_ztf_data = found_ztf_data.filter(Ztf.seeing < seeing)

        if objid > 0:
            found_ztf_data = (
                found_ztf_data
                .filter(Found.objid == objid)
                .order_by(Found.obsjd)
            )

        found_ztf_data = (
            found_ztf_data
            .offset(start_row)
            .limit(500 if end_row == -1 else end_row - start_row)
        )

    # unpack into list of dictionaries for marshalling
    data = []
    print(found_ztf_data[0]._asdict())
    for row in found_ztf_data:
        data.append(row._asdict())

    return data


def query_ztf_nights_metadata() -> Any:
    """Return ZTF nights table metadata."""

    description: Dict[str, str] = {
        'nightid': 'unique night identifier',
        'date': 'date (UT)',
        'exposures': 'number of exposures',
        'quads': 'number of quads'
    }
    return description


def query_ztf_nights_data(start_row: int=0, end_row: int=-1, nightid: int=-1,
                          date: str='') -> Any:
    '''Query DB for ZTF nights'''
    ztf_nights_data: Any

    with DATA_PROVIDER_SESSION() as session:
        ztf_nights_data = session.query(ZtfNight)

        if nightid > 0:
            ztf_nights_data = ztf_nights_data.filter(
                ZtfNight.nightid == nightid)
        elif date != '':
            ztf_nights_data = ztf_nights_data.filter(ZtfNight.date == date)

        ztf_nights_data = (
            ztf_nights_data
            .order_by(ZtfNight.nightid.desc())
            .offset(start_row)
            .limit(500 if end_row == -1 else end_row - start_row)
        )

        serialized_row: Dict[str, Any] = {}
        all_serialized_rows: List[dict] = []
        for row in ztf_nights_data:
            serialized_row = {
                "nightid": row.nightid,
                "date": row.date,
                "exposures": row.exposures,
                "quads": row.quads
            }

            # Convert items in binary row to tpython data structures
            for key, val in serialized_row.items():
                if isinstance(val, Decimal):
                    serialized_row[key] = float(val)
                elif isinstance(val, int):
                    serialized_row[key] = int(val)
                else:
                    serialized_row[key] = str(val)
            all_serialized_rows.append(serialized_row)

    return all_serialized_rows
