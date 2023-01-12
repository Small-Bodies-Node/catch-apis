from typing import Union, List
import uuid
import logging

from sbsearch.exceptions import SBSException
from catch.exceptions import CatchException

from ..services.catch_manager import catch_manager
from ..services.message import (Message, listen_for_task_messages,
                                stop_listening_for_task_messages,
                                TaskStatus)
from ..config.logging import get_logger

# List of surveys to search, and those to search by default.  The `catch`
# library default is to search all survey sources, but we force `catch-apis` to
# be specific.  This avoids the `catch` library searching data sources that may
# be in development or otherwise not yet released to the public.
QUERY_SOURCES_ALLOWED: List[str] = [
    'neat_palomar_tricam',
    'neat_maui_geodss',
    'skymapper',
    'ps1dr2',
    'catalina_bigelow',
    'catalina_lemmon',
    'catalina_bokneosurvey',
]

# As of Jan 2023, there is no data in the Bok NEO Survey, so no need to list it
# here:
QUERY_SOURCES_DEFAULT: List[str] = [
    'neat_palomar_tricam',
    'neat_maui_geodss',
    'skymapper',
    'ps1dr2',
    'catalina_bigelow',
    'catalina_lemmon',
]


def catch_moving_target(job_id: uuid.UUID, target: str,
                        sources: Union[List[str], None],
                        uncertainty_ellipse: bool, padding: float,
                        cached: bool) -> None:
    """Search for target in CATCH surveys.


    Parameters
    ----------
    job_id : uuid.UUID
        Unique ID for job.

    target : string
        Target target.

    sources : list of strings or None
        Names of observation sources to search or ``None`` to search all
        sources.

    uncertainty_ellipse : bool
        Search using the ephemeris uncertainty ellipse.

    padding : bool
        Additional padding around the ephemeris search region, arcmin.

    cached : bool
        ``True`` to use cached results.

    """

    logger: logging.Logger = get_logger()

    # subscribe the logger and task messenger to this job_id
    listen_for_task_messages(job_id)

    msg: Message = Message(
        job_id, status='running',
        text='Starting moving target query.'
    )
    msg.publish()

    _sources: List[str] = QUERY_SOURCES_DEFAULT if sources is None else sources

    exc: Exception
    try:
        with catch_manager() as catch:
            catch.uncertainty_ellipse = uncertainty_ellipse
            catch.padding = padding
            catch.query(target, job_id, sources=_sources,
                        cached=cached)

        msg.status = TaskStatus.SUCCESS
        msg.text = 'Task complete.'
    except (CatchException, SBSException) as exc:
        logger.exception("catch error.")
        msg.status = TaskStatus.ERROR
        msg.text = str(exc)
    except Exception:
        logger.exception("An unexpected error occurred.")
        msg.status = TaskStatus.ERROR
        msg.text = 'An unexpected error occurred.  Contact us if this problem persists.'
    finally:
        msg.publish()
        stop_listening_for_task_messages(job_id)
