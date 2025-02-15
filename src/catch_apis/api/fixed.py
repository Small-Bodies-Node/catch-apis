# Licensed with the 3-clause BSD license.  See LICENSE for details.

import json
import uuid
import logging

from astropy.coordinates import Angle

from ..validation import parse_ra, parse_dec, parse_date
from ..services.fixed import fixed_target_query_service
from ..config import CatchApisException, get_logger, allowed_sources
from .. import __version__ as version


def _format_date(date):
    return date if date is None else date.iso


def invalid_query(messages: list[str]) -> dict:
    """Form the response for an invalid query."""
    logger = get_logger()
    result = {
        "error": True,
        "message": "  ".join(messages),
        "version": version,
    }
    logger.info(json.dumps(result))
    return result


def fixed_target_query_controller(
    ra: str,
    dec: str,
    sources: list[str] | None = None,
    start_date: str | None = None,
    stop_date: str | None = None,
    radius: float = 0,
    intersection_type: str = "ImageIntersectsArea",
) -> dict:
    """Controller for fixed target queries.

    Parameters
    ----------
    ra : string
        Right ascension, sexagesimal or decimal format.  If the unit is
        unspecified and the string is parsable as a decimal value, then degree
        is assumed, hour angle otherwise.

    dec : string
        Declination, sexagesimal or decimal format.  If the unit is unspecified
        then degree is assumed.

    sources : list of str, optional
        Search these sources, or else all sources.

    start_date : str, optional
        Search after this date.  Strings are parsed with `astropy.time.Time`.

    stop_date : str, optional
        Search before this date.  Strings are parsed with `astropy.time.Time`.

    radius: float, optional
        Areal search around the coordinates, arcmin.

    intersection_type : str
        Type of intersections to allow between search area and data.  See
        `catch.IntersectionType` for valid names.

    """

    logger = get_logger()
    job_id = uuid.uuid4()
    messages = []
    valid_query = True  # assume valid until it isn't

    # default: search all sources allowed in the API spec
    # but, the user may have requested specific sources
    _sources = allowed_sources if sources is None else sources

    try:
        sanitized_ra = parse_ra(ra)
        sanitized_dec = parse_dec(dec)
    except ValueError as exc:
        messages.append(str(exc))
        valid_query = False

    try:
        sanitized_start_date = parse_date(start_date, "start")
        sanitized_stop_date = parse_date(stop_date, "stop")
    except ValueError as exc:
        messages.append(str(exc))
        valid_query = False

    if not valid_query:
        return invalid_query(messages)

    data = []
    try:
        data = fixed_target_query_service(
            job_id,
            sanitized_ra,
            sanitized_dec,
            sources,
            sanitized_start_date,
            sanitized_stop_date,
            radius,
            intersection_type,
        )
    except CatchApisException as exc:
        logger.exception("Error during fixed target query.")
        messages.append(str(exc))
        return invalid_query(messages)
    except:
        logger.exception("Unexpected error during fixed target query.")
        messages.append(
            "Unexpected error.  Please contact us with the details of your query."
        )
        return invalid_query(messages)

    # add data to the result after logging
    result = {
        "message": "  ".join(messages),
        "version": version,
        "query": {
            "ra": sanitized_ra.deg,
            "dec": sanitized_dec.deg,
            "sources": _sources,
            "start_date": _format_date(sanitized_start_date),
            "stop_date": _format_date(sanitized_stop_date),
            "radius": radius,
            "intersection_type": intersection_type,
        },
        "count": len(data),
    }

    logger.info(json.dumps(result))
    result["data"] = data
    return result
