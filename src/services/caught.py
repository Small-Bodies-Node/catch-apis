"""Caught moving object data services."""
import uuid
from typing import List, Dict, Union

from sqlalchemy.inspection import inspect
from catch.schema import Found, Obs, Obj, Caught, CatchQueries

from util import desg_to_prefix
from env import ENV
from . import images
from .database_provider import data_provider_session, Session


def caught(job_id: uuid.UUID) -> List[dict]:
    """Caught object results.

    Parameters
    ----------
    job_id : uuid.UUID
        Unique job id for the search.

    """

    # unpack into list of dictionaries for marshaling
    found: List[Dict[str, Union[Found, Obs, Obj, str, float, int, bool, None]]]
    found = []

    session: Session
    with data_provider_session() as session:
        data = (session.query(Found, Obs, Obj)
                .join(Caught, Found.foundid == Caught.foundid)
                .join(CatchQueries, CatchQueries.queryid == Caught.queryid)
                .join(Obs, Found.obsid == Obs.obsid)
                .join(Obj, Found.objid == Obj.objid)
                .filter(CatchQueries.jobid == job_id.hex))

        for row in data:
            found.append({})
            for table in row:
                fields: dict = {}
                for k in dir(type(table)):
                    if k.startswith('_'):
                        continue
                    fields[k] = getattr(table, k)
                found[-1][table.__class__.__name__] = fields

            # some extras
            # cutout around target
            cutout_url: str = images.build_cutout_url(
                row, size=5, prefix=desg_to_prefix(row.Obj.desg) + '_')
            found[-1]['cutout_url'] = cutout_url

            # preview image
            if row.Obs.source[:4] == 'neat':
                found[-1]['thumbnail_url'] = (
                    cutout_url
                    .replace(ENV.CATCH_CUTOUT_BASE_URL,
                             ENV.CATCH_THUMBNAIL_BASE_URL)
                    .replace('.fits', '_thumb.jpg')
                )
            elif row.Obs.source == 'skymapper':
                found[-1]['thumbnail_url'] = str(found[-1]['cutout_url']).replace(
                    'fits', 'png')

            # full-frame image
            found[-1]['archive_url'] = images.build_fullframe_url(row)

    return found
