import os
import uuid
import json
import urllib.parse

from flask import request
from astropy.time import Time

from ..config import allowed_sources, get_logger, QueryStatus
from ..validation import parse_target_name
from ..services.catch import catch_service
from ..services.status.queue import queue_service
from ..services.message import (
    Message,
    listen_for_task_messages,
    stop_listening_for_task_messages,
)
from .. import __version__ as version


def _parse_date(date: str | None, kind: str) -> str | None:
    sanitized_date = None
    try:
        sanitized_date = None if date is None else Time(date)
    except ValueError:
        raise ValueError(f"Invalid {kind}_date: {date}")

    return sanitized_date


def _format_date(date):
    return date if date is None else date.iso


def catch_controller(
    target: str,
    sources: list[str] | None = None,
    start_date: str | None = None,
    stop_date: str | None = None,
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

    logger = get_logger()
    job_id = uuid.uuid4()
    messages = []
    valid_query = True

    target_type, sanitized_target = parse_target_name(target)
    if target.strip() == "":
        messages.append("Invalid target: empty string")
        valid_query = False
    elif sanitized_target == "":
        messages.append(
            "Target names may be ambiguous (e.g., Encke is the name of a comet and "
            "an asteroid) and are not supported.  Use the target's designation or "
            "permanent catalog ID (e.g., 2P or 9134)."
        )
        valid_query = False

    # default: search all sources allowed in the API spec
    # but, the user may have requested specific sources
    _sources = allowed_sources if sources is None else sources

    try:
        sanitized_start_date = _parse_date(start_date, "start")
        sanitized_stop_date = _parse_date(stop_date, "stop")
    except ValueError as exc:  # noqa F841
        messages.append(str(exc))
        valid_query = False

    if not valid_query:
        # then just stop now
        result = {
            "error": True,
            "queued": False,
            "message": "  ".join(messages),
            "version": version,
        }
        logger.info(json.dumps(result))
        return result

    # otherwise, we can proceed with the search
    result = {
        "query": {
            "target": sanitized_target,
            "type": target_type.value,
            "sources": _sources,
            "start_date": _format_date(sanitized_start_date),
            "stop_date": _format_date(sanitized_stop_date),
            "cached": cached,
            "uncertainty_ellipse": uncertainty_ellipse,
            "padding": padding,
        },
        "job_id": job_id.hex,
        "error": False,
        "queued": False,
        "queue_full": False,
        "queue_position": None,
        "message": None,
        "version": version,
    }

    Message.reset_t0()
    listen_for_task_messages(job_id)

    status = catch_service(
        job_id,
        sanitized_target,
        sources=_sources,
        start_date=sanitized_start_date,
        stop_date=sanitized_stop_date,
        uncertainty_ellipse=uncertainty_ellipse,
        padding=padding,
        cached=cached,
    )

    parsed = urllib.parse.urlsplit(request.url_root)
    results_url = urllib.parse.urlunsplit(
        (parsed[0], parsed[1], os.path.join(parsed[2], "caught", job_id.hex), "", "")
    )
    message_stream_url = urllib.parse.urlunsplit(
        (parsed[0], parsed[1], os.path.join(parsed[2], "stream"), "", "")
    )

    if status == QueryStatus.QUEUED:
        for job in queue_service()["jobs"]:
            if job["prefix"] == job_id.hex[:8]:
                result["queue_position"] = job["position"]
                break

        result["queued"] = True
        result["message_stream"] = message_stream_url
        result["results"] = results_url
        messages.append(
            "Enqueued search.  Listen to task messaging stream until job "
            "completed, then retrieve data from results URL."
        )
    elif status == QueryStatus.QUEUEFULL:
        result["error"] = True
        result["queued"] = False
        result["queue_full"] = True
        messages.append("Queue is full, please try again later.")
    else:
        # status.SUCCESS
        result["queued"] = False
        result["results"] = results_url
        messages.append("Found cached data.  Retrieve from results URL.")

    result["message"] = "  ".join(messages)
    logger.info(json.dumps(result))
    stop_listening_for_task_messages(job_id)
    return result
