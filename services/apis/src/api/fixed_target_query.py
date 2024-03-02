import os
import json
import uuid
import logging
from typing import Optional, List
from connexion import request
from ..services import fixed_target_query as query
from ..config.exceptions import CatchApisException
from ..config.logging import get_logger
from .. import __version__


def point(ra: str, dec: str, sources: Optional[List[str]] = None) -> dict:
    """Controller for fixed target queries.

    Parameters
    ----------
    ra : string
        Right ascension, units of hour angle.

    dec : string
        Declination, units of deg.

    sources : list of str, optional
        Search these sources, or else all sources.

    """

    from ..api.app import allowed_sources, version  # avoid circular import

    logger: logging.Logger = get_logger()
    job_id: uuid.UUID = uuid.uuid4()

    # default: search all sources allowed in the API spec
    _sources: List[str] = allowed_sources

    # but, the user may have requested specific sources
    if sources is not None:
        _sources = sources

    data: List[dict] = []
    message: str = ""
    try:
        data = query.point(job_id, ra, dec, sources)
    except CatchApisException as e:
        message = str(e)

    result: dict = {
        "message": message,
        "version": version,
        "query": {
            "ra": ra,
            "dec": dec,
            "sources": _sources,
        },
    }
    logger.info(json.dumps(result))

    result["data"] = data
    return result
