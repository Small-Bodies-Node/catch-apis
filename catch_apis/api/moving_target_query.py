
import os
import uuid
import json
import urllib.parse
import logging
from typing import Optional, List
from connexion import request
from .. import services
from ..logging import get_logger


def moving_target_query(target: str, source: Optional[List[str]] = None,
                        uncertainty_ellipse: bool = False,
                        padding: float = 0, cached: bool = False) -> dict:
    """Controller for target queries."""

    logger: logging.Logger = get_logger()
    job_id: uuid.UUID = uuid.uuid4()

    result: dict = {
        'query': {
            'target': target,
            'source': source,
            'cached': cached,
            'uncertainty_ellipse': uncertainty_ellipse,
            'padding': padding
        },
        'job_id': job_id.hex,
        'version': '2.0.0'
    }

    status: services.QueryStatus
    status, result['queue_full'] = services.moving_target_query(
        job_id, target, source, cached)

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
        result['message'] = ('Enqueued search.  Listen to task messaging stream until'
                             ' job completed, then retrieve data from results URL.')

    elif status == services.QueryStatus.QUEUEFULL:
        result['queued'] = False
        result['message'] = 'Queue is full, please try again later.'
    else:
        # status.SUCCESS
        result['queued'] = False
        result['message'] = 'Found cached data.  Retrieve from results URL.'

    logger.info(json.dumps(result))
    return result
