'''Query DB for ZTF data'''

from typing import List
import sqlalchemy as sa
from models import ztf
from .database_provider import DATA_PROVIDER_SESSION


def found_objects() -> List[dict]:
    """Return ZTF found object list."""
    query: sa.orm.Query

    with DATA_PROVIDER_SESSION() as session:
        # cast to float or else:
        # TypeError: Object of type 'Decimal' is not JSON serializable
        query = (
            session.query(
                ztf.Found.objid,
                ztf.Obj.desg,
                sa.cast(sa.func.min(ztf.Found.obsjd), sa.Float)
                .label('obsjd_min'),
                sa.cast(sa.func.max(ztf.Found.obsjd), sa.Float)
                .label('obsjd_max')
            )
            .join(ztf.Obj, ztf.Obj.objid == ztf.Found.objid)
            .group_by(ztf.Found.objid)
            .order_by(ztf.Obj.desg + 0, ztf.Obj.desg)
        )

    # unpack into list of dictionaries for marshalling
    rows: List[dict] = []
    for row in query:
        rows.append(row._asdict())

    return rows


def found(start_row: int = 0, end_row: int = -1, objid: int = -1,
          nightid: int = -1, maglimit: float = 0,
          seeing: float = 0, foundid: int = -1) -> List[dict]:
    '''Query DB for ZTF found data.'''
    query: sa.orm.Query

    print("\n\n>>>>>>>>>>>>>>>\n\n")

    with DATA_PROVIDER_SESSION() as session:
        query = (
            session
            .query(
                ztf.Found,
                ztf.Ztf,
                ztf.ZtfCutout,
                sa.func.substr(sa.cast(ztf.Ztf.filefracday, sa.String), 1, 4)
                .label('year'),
                sa.func.substr(sa.cast(ztf.Ztf.filefracday, sa.String), 5, 4)
                .label('monthday'),
                sa.func.substr(sa.cast(ztf.Ztf.filefracday, sa.String), 9)
                .label('fracday')
            )
            .join(ztf.Ztf, ztf.Found.obsid == ztf.Ztf.obsid)
            # the cutout may not exist, use left outer join:
            .outerjoin(
                ztf.ZtfCutout,
                ztf.Found.foundid == ztf.ZtfCutout.foundid
            )
        )

        print("\n\n>>>>>>> 2 >>>>>>>>\n\n")

        if maglimit > 0:
            query = query.filter(ztf.Ztf.maglimit > maglimit)

        if nightid > 0:
            query = query.filter(ztf.Ztf.nightid == nightid)

        if seeing > 0:
            query = query.filter(ztf.Ztf.seeing < seeing)

        if objid > 0:
            query = (
                query.filter(ztf.Found.objid == objid)
                .order_by(ztf.Found.obsjd)
            )

        if foundid > 0:
            query = query.filter(ztf.Found.foundid == foundid)
        else:
            query = (
                query.offset(start_row)
                .limit(500 if end_row == -1 else end_row - start_row)
            )

    # unpack into list of dictionaries for marshalling
    rows: List[dict] = []
    for row in query:
        rows.append(row._asdict())

    return rows


def nights(start_row: int = 0, end_row: int = -1, nightid: int = -1,
           date: str = '') -> List[dict]:
    '''Query DB for ZTF nights'''
    query: sa.orm.Query

    with DATA_PROVIDER_SESSION() as session:
        query = session.query(ztf.ZtfNights)

        if nightid > 0:
            query = query.filter(ztf.ZtfNights.nightid == nightid)
        elif date != '':
            query = query.filter(ztf.ZtfNights.date == date)

        query = (
            query.order_by(ztf.ZtfNights.nightid.desc())
            .offset(start_row)
            .limit(500 if end_row == -1 else end_row - start_row)
        )

    # unpack into list of dictionaries for marshalling
    rows: List[dict] = []
    for row in query:
        rows.append(row.__dict__)

    return rows
