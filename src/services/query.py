"""
Catch a moving target in survey data.
"""

from typing import List, Any
import uuid

from .caught import caught
from .database_provider import catch_manager


def query(target: str, job_id: uuid.UUID, source: str,
          cached: bool) -> List[Any]:
    """Run query and return caught data.


    Parameters
    ----------
    target : string
        Target for which to search.

    job_id : uuid.UUID
        Unique job ID.

    source : string
        Observation source.

    cached : bool
        OK to return cached results?


    Returns
    -------
    found : list
        Found observations and metadata.

    """
    with catch_manager(save_log=True) as catch:
        catch.query(target, job_id, source=source, cached=cached)

    found = caught(job_id)
    return found


def check_cache(target: str, source: str) -> bool:
    """Check CATCH cache for previous query.


    Parameters
    ----------
    target : string
        Target name.

    source : string
        Observation source or ``'any'``.


    Returns
    -------
    cached : bool

        ``True`` if ``source`` has already been searched for
        ``target``.  When ``source`` is ``'any'``, then if any source
        was not searched, ``cached`` will be ``False``.

    """

    with catch_manager(save_log=False) as catch:
        cached = catch.check_cache(target, source=source)
    return cached
