import uuid
from typing import Any, Dict, List, Union

from catch.model import Found, Observation
from . import marshal
from .catch_manager import Catch, catch_manager


def caught_service(job_id: uuid.UUID) -> List[Dict[str, Any]]:
    """Caught object results.


    Parameters
    ----------
    job_id : uuid.UUID
        Unique job id for the search.


    Return
    ------
    data : list of dict

    """

    # unpack into list of dictionaries for serialization
    data: List[Dict[str, Any]] = []

    catch: Catch
    with catch_manager() as catch:
        found_observations: List[Any] = catch.caught(job_id)

        found: Found
        obs: Observation
        for found, obs in found_observations:
            row: Dict[str, Union[str, float, int, None]] = marshal.observation(
                obs, found.ra, found.dec
            )
            row.update(marshal.found(found))
            data.append(row)

    return data
