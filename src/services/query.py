"""
Catch a moving target in survey data.
"""

import re
from typing import List, Any, Optional, Callable
import uuid

from sbpy.data.names import Names, TargetNameParseError

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


def check_cache(target: str, source: str,
                save_to: Optional[uuid.UUID]) -> bool:
    """Check CATCH cache for previous query.


    Parameters
    ----------
    target : string
        Target name.

    source : string
        Observation source or ``'any'``.

    save_to : UUID, optional
        Save the cached query under this job ID.


    Returns
    -------
    cached : bool
        ``True`` if ``source`` has already been searched for
        ``target``.  When ``source`` is ``'any'``, then if any source
        was not searched, ``cached`` will be ``False``.

    """

    with catch_manager(save_log=False) as catch:
        cached = catch.check_cache(target, source=source)
        if cached and (save_to is not None):
            catch.query(target, save_to, source=source, cached=True)
    return cached


def parse_target_name(name: str) -> str:
    """Parse moving target name.


    Parameters
    ----------
    name : str
        String to test.


    Returns
    -------
    target_type : str
        'asteroid', 'comet', or 'unknown'.

    """

    parser: Callable
    target_type: str
    if re.match('(^[PCDXA]/)|(^[0-9]+[PD])', name):
        parser = Names.parse_comet
        target_type = 'comet'
    else:
        parser = Names.parse_asteroid
        target_type = 'asteroid'

    try:
        parser(name)
        if target_type.startswith('A/'):
            # in sbpy v0.1.1, this parses as a comet but should be asteroid
            target_type = 'asteroid'
    except TargetNameParseError:
        target_type = 'unknown'

    return target_type
