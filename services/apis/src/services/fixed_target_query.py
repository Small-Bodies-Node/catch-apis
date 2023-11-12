"""Service provider for fixed target queries."""

from uuid import UUID
from typing import List, Optional
from sbsearch.target import FixedTarget
from catch.model import CatchQuery, Observation
from .catch_manager import catch_manager
from . import marshal


def point(job_id: UUID, ra: str, dec: str, sources: Optional[List[str]]) -> List[dict]:
    """Search the database for a single point.


    Parameters
    ----------
    job_id : `UUID`
        Unique job identifier.

    ra : string
        Right ascension, units of hour angle.

    dec : string
        Declination, units of deg.

    sources : list of str, optional
        Search these sources, or else all sources.


    Returns
    -------
    data : list
        Found observations.

    """

    from ..api.app import allowed_sources  # avoid circular import

    target: FixedTarget = FixedTarget.from_radec(
        ra, dec, unit=("hourangle", "deg"))

    observations: List[Observation] = []
    data: List[dict]
    with catch_manager() as catch:
        observations = catch.query(target, job_id, sources)
        # queries: List[CatchQuery] = catch.queries_from_job_id(job_id)
        data = [marshal.observation(
            obs, target.ra.deg, target.dec.deg) for obs in observations]

    return data
