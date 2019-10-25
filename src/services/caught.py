"""Caught moving object data services."""
import uuid
from typing import List
from catch.schema import Found, Obs, Obj, Caught, CatchQueries
from .database_provider import data_provider_session


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

    # unpack into list of dictionaries for marshalling
    found: List[dict] = []
    for row in data:
        found.append(row._asdict())

        # some extras
        # rows[-1]['cutout_url'] = ...
        # rows[-1]['fullframe_url'] = ...

    return found
