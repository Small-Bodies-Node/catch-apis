
import os
import uuid
import json
import urllib.parse
import logging
from typing import Optional, List
from connexion import request
from .. import services
from ..config.logging import get_logger
from .. import __version__


def moving_target_query(target: str, sources: Optional[List[str]] = None,
                        uncertainty_ellipse: bool = False,
                        padding: float = 0, cached: bool = False) -> dict:
    """Controller for target queries.

    Parameters
    ----------
    target : string
        The target target.

    sources : list of str, optional
        Search these sources, or else all sources.

    uncertainty_ellipse : bool, optional
        Search using the ephemeris uncertainty ellipse.

    padding : bool, optional
        Additional padding around the ephemeris search region, arcmin.

    cached : bool, optional
        ``True`` if it is OK to return cached results.

    """

    logger: logging.Logger = get_logger()
    job_id: uuid.UUID = uuid.uuid4()

    target_type: str
    sanitized_target: str
    target_type, sanitized_target = services.parse_target_name(target)

    result: dict = {
        'query': {
            'target': sanitized_target,
            'type': target_type,
            'sources': sources,
            'cached': cached,
            'uncertainty_ellipse': uncertainty_ellipse,
            'padding': padding
        },
        'job_id': job_id.hex,
        'queued': None,
        'message': None,
        'version': __version__
    }

    status: services.QueryStatus
    status = services.moving_target_query(
        job_id, sanitized_target, sources=sources,
        uncertainty_ellipse=uncertainty_ellipse,
        padding=padding, cached=cached)

    parsed: tuple = urllib.parse.urlsplit(request.url_root)
    result['results'] = urllib.parse.urlunsplit((
        parsed[0], parsed[1], os.path.join(parsed[2], 'caught', job_id.hex),
        '', ''
    ))
    result['message_stream'] = urllib.parse.urlunsplit((
        parsed[0], parsed[1],
        os.path.join(parsed[2], 'stream'),
        '', ''
    ))

    if status == services.QueryStatus.QUEUED:
        result['queued'] = True
        result['message'] = (
            'Enqueued search.  Listen to task messaging stream until job '
            'completed, then retrieve data from results URL.'
        )

    elif status == services.QueryStatus.QUEUEFULL:
        result['queued'] = False
        result['message'] = 'Queue is full, please try again later.'
    else:
        # status.SUCCESS
        result['queued'] = False
        result['message'] = 'Found cached data.  Retrieve from results URL.'

    logger.info(json.dumps(result))
    return result
