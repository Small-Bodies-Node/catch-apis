"""Service provider for fixed target queries."""

from uuid import UUID
from typing import List, Union

from astropy.time import Time
from astropy.coordinates import Angle
from sbsearch.target import FixedTarget
from catch import IntersectionType
from catch.model import Observation

from ..config import allowed_sources
from .catch_manager import catch_manager
from . import marshal


def fixed_target_query_service(
    job_id: UUID,
    ra: Angle,
    dec: Angle,
    sources: Union[List[str], None],
    start_date: Union[str, None],
    stop_date: Union[str, None],
    radius: float,
    intersection_type: str,
) -> List[dict]:
    """Search the database for a single point.


    Parameters
    ----------
    job_id : `UUID`
        Unique job identifier.

    ra : astropy.coordinates.Angle
        Right ascension.

    dec : astropy.coordinates.Angle
        Declination.

    sources : list of str or ``None``
        Search these sources, or else ``None`` to search all sources.

    start_date : Time or None
        Search after this date.  Strings are parsed with `astropy.time.Time`.

    stop_date : Time or None
        Search before this date.  Strings are parsed with `astropy.time.Time`.

    radius: float
        Areal search around the coordinates, arcmin.

    intersection_type : str
        Type of intersections to allow between search area and data.  See
        `catch.IntersectionType` for valid names.


    Returns
    -------
    data : list
        Found observations.

    """

    target: FixedTarget = FixedTarget.from_radec(ra, dec)

    observations: List[Observation] = []
    data: List[dict]
    with catch_manager() as catch:
        catch.start_date = start_date
        catch.stop_date = stop_date
        catch.padding = min(max(radius, 0), 600)
        catch.intersection_type = IntersectionType[intersection_type]
        observations = catch.query(target, job_id, sources)
        data = [
            marshal.observation(obs, target.ra.deg, target.dec.deg)
            for obs in observations
        ]

    return data
