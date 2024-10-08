import os
import uuid
import json
import urllib.parse
import logging
from typing import List, Optional, Union

from flask import request
from astropy.time import Time

from ..config import allowed_sources, get_logger, QueryStatus
from .. import services
from .. import __version__ as version


def _parse_date(date: Union[str, None], kind: str) -> Union[str, None]:
    sanitized_date: Union[str, None] = None
    try:
        sanitized_date = None if date is None else Time(date)
    except ValueError:
        raise ValueError(f"Invalid {kind}_date: {date}")

    return sanitized_date

def _format_date(date):
    return date if date is None else date.iso

def catch(
    target: str,
    sources: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    stop_date: Optional[str] = None,
    uncertainty_ellipse: bool = False,
    padding: float = 0,
    cached: bool = True,
):
    """Controller for moving target queries.

    Parameters
    ----------
    target : string
        The target target.

    sources : list of str, optional
        Search these sources, or else all sources.

    start_date : str, optional
        Search after this date/time.

    stop_date : str, optional
        Search before this date/time.

    uncertainty_ellipse : bool, optional
        Search using the ephemeris uncertainty ellipse.

    padding : bool, optional
        Additional padding around the ephemeris search region, arcmin.

    cached : bool, optional
        ``True`` if it is OK to return cached results.

    """

    logger: logging.Logger = get_logger()
    job_id: uuid.UUID = uuid.uuid4()
    messages: List[str] = []
    valid_query: bool = True

    target_type: str
    sanitized_target: str
    target_type, sanitized_target = services.parse_target_name(target)

    # default: search all sources allowed in the API spec
    # but, the user may have requested specific sources
    _sources: List[str] = allowed_sources if sources is None else sources

    exc: Exception
    try:
        sanitized_start_date: Union[str, None] = _parse_date(start_date, "start")
        sanitized_stop_date: Union[str, None] = _parse_date(stop_date, "stop")
    except ValueError as exc:
        messages.append(str(exc))
        valid_query = False


    if not valid_query:
        # then just stop now
        result: dict = {
            "queued": False,
            "message": "  ".join(messages),
            "version": version,
        }
        logger.info(json.dumps(result))
        return result

    # otherwise, we can proceed with the search
    result: dict = {
        "query": {
            "target": sanitized_target,
            "type": target_type,
            "sources": _sources,
            "start_date": _format_date(sanitized_start_date),
            "stop_date": _format_date(sanitized_stop_date),
            "cached": cached,
            "uncertainty_ellipse": uncertainty_ellipse,
            "padding": padding,
        },
        "job_id": job_id.hex,
        "queued": None,
        "message": None,
        "version": version,
    }

    status: QueryStatus = services.catch(
        job_id,
        sanitized_target,
        sources=_sources,
        start_date=sanitized_start_date,
        stop_date=sanitized_stop_date,
        uncertainty_ellipse=uncertainty_ellipse,
        padding=padding,
        cached=cached,
    )

    parsed: tuple = urllib.parse.urlsplit(request.url_root)
    result["results"] = urllib.parse.urlunsplit(
        (parsed[0], parsed[1], os.path.join(parsed[2], "caught", job_id.hex), "", "")
    )
    result["message_stream"] = urllib.parse.urlunsplit(
        (parsed[0], parsed[1], os.path.join(parsed[2], "stream"), "", "")
    )

    if status == QueryStatus.QUEUED:
        result["queued"] = True
        messages.append(
            "Enqueued search.  Listen to task messaging stream until job "
            "completed, then retrieve data from results URL."
        )
    elif status == QueryStatus.QUEUEFULL:
        result["queued"] = False
        messages.append("Queue is full, please try again later.")
    else:
        # status.SUCCESS
        result["queued"] = False
        messages.append("Found cached data.  Retrieve from results URL.")

    result["message"] = "  ".join(messages)
    logger.info(json.dumps(result))
    return result
