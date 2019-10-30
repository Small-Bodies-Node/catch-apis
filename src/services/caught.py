"""Caught moving object data services."""
import uuid
from typing import List, Dict, Union, Iterator

from catch.schema import Found, Obs, Obj, Caught, CatchQueries

from . import images
from .database_provider import data_provider_session, Session
# from sqlalchemy.orm.session import Session, sessionmaker
from util import desg_to_prefix
from env import ENV


def caught(job_id: uuid.UUID) -> List[dict]:
    """Caught object results.

    Parameters
    ----------
    job_id : uuid.UUID
        Unique job id for the search.

    """

    with data_provider_session() as session:
        data = (session.query(Found, Obs, Obj)
                .join(Caught, Found.foundid == Caught.foundid)
                .join(CatchQueries, CatchQueries.queryid == Caught.queryid)
                .join(Obs, Found.obsid == Obs.obsid)
                .join(Obj, Found.objid == Obj.objid)
                .filter(CatchQueries.jobid == job_id.hex))
        session.expunge_all()

    # unpack into list of dictionaries for marshaling
    found: List[Dict[str, Union[Found, Obs, Obj, str, float, int, bool, None]]]
    found = []
    for row in data:
        found.append(row._asdict())

        # some extras
        cutout_url: str = images.build_url(
            row.Obs.productid, ra=row.Found.ra, dec=row.Found.dec,
            size=5, prefix=desg_to_prefix(row.Obj.desg) + '_')
        found[-1]['cutout_url'] = cutout_url
        found[-1]['thumbnail_url'] = cutout_url \
            .replace(ENV.CATCH_CUTOUT_BASE_URL, ENV.CATCH_THUMBNAIL_BASE_URL) \
            .replace('.fits', '_thumb.jpg')
        found[-1]['archive_url'] = images.build_url(row.Obs.productid)

    return found
