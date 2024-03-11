import json
import uuid
import logging
from typing import List, Optional, Union

from astropy.time import Time
from astropy.coordinates import Angle
import astropy.units as u

from .. import services
from ..config import CatchApisException, get_logger, allowed_sources
from .. import __version__ as version


def _parse_ra(ra: str) -> Angle:
    """Raise ValueError if cannot be parsed."""

    try:
        float(ra)
    except ValueError:
        ra_unit = u.hourangle

    try:
        sanitized_ra: Angle = Angle(ra, ra_unit)
    except Exception as e:
        raise ValueError(f"Invalid ra: {ra}")
    
    return sanitized_ra

def _parse_dec(dec: str) -> Angle:
    """Raise ValueError if cannot be parsed."""

    sanitized_dec: Angle
    try:
        sanitized_dec = Angle(dec)
    except u.UnitsError:
        try:
            sanitized_dec = Angle(dec, u.deg)
        except Exception as e:
            raise ValueError(f"Invalid dec: {dec}")
    except ValueError as e:
        raise ValueError(f"Invalid dec: {dec}")
    
    return sanitized_dec

def _parse_date(date: Union[str, None], kind: str) -> Union[str, None]:
    sanitized_date: Union[str, None] = None
    try:
        sanitized_date = None if date is None else Time(date)
    except ValueError:
        raise ValueError(f"Invalid {kind}_date: {date}")

    return sanitized_date

def _format_date(date):
    return date if date is None else date.iso


def fixed_target_query(
    ra: str,
    dec: str,
    sources: Optional[List[str]] = None,
    start_date: Optional[str] = None,
    stop_date: Optional[str] = None,
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

    logger: logging.Logger = get_logger()
    job_id: uuid.UUID = uuid.uuid4()
    messages: List[str] = []

    # default: search all sources allowed in the API spec
    # but, the user may have requested specific sources
    _sources: List[str] = allowed_sources if sources is None else sources

    valid_query: bool = True

    exc: Exception
    try:
        sanitized_ra: Angle = _parse_ra(ra)
        sanitized_dec: Angle = _parse_dec(dec)
    except ValueError as exc:
        messages.append(str(exc))
        valid_query = False

    try:
        sanitized_start_date: Union[str, None] = _parse_date(start_date, "start")
        sanitized_stop_date: Union[str, None] = _parse_date(stop_date, "stop")
    except ValueError as exc:
        messages.append(str(exc))
        valid_query = False

    data: List[dict] = []
    if valid_query:
        try:
            data = services.fixed_target_query(
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
            messages.append(str(exc))

    result: dict = {
        "message": "  ".join(messages),
        "version": version,
    }

    if valid_query:
        # only append if the query seems valid otherwise the angles and dates
        # may not be defined
        result["query"] = {
            "ra": sanitized_ra.deg,
            "dec": sanitized_dec.deg,
            "sources": _sources,
            "start_date": _format_date(sanitized_start_date),
            "stop_date": _format_date(sanitized_stop_date),
            "radius": radius,
            "intersection_type": intersection_type,
        }

    logger.info(json.dumps(result))
    result["data"] = data
    return result
