from typing import Union, List
import uuid
import logging

from astropy.time import Time
from sbsearch.exceptions import SBSException
from catch.exceptions import CatchException

from ..services.catch_manager import catch_manager
from ..services.message import (
    Message,
    listen_for_task_messages,
    stop_listening_for_task_messages,
    TaskStatus,
)
from ..config import get_logger, allowed_sources


def catch(
    job_id: uuid.UUID,
    target: str,
    sources: Union[List[str], None],
    start_date: Union[str, None],
    stop_date: Union[str, None],
    uncertainty_ellipse: bool,
    padding: float,
    cached: bool,
) -> None:
    """Search for target in CATCH surveys.


    Parameters
    ----------
    job_id : uuid.UUID
        Unique ID for job.

    target : string
        The target target.

    sources : list of str
        Search these sources, or, if ``None``, all sources.

    start_date : str or None
        Search after this date/time.

    stop_date : str or None
        Search after this date/time.

    uncertainty_ellipse : bool
        Search using the ephemeris uncertainty ellipse.

    padding : bool
        Additional padding around the ephemeris search region, arcmin.

    cached : bool
        ``True`` if it is OK to return cached results.

    """

    logger: logging.Logger = get_logger()

    # subscribe the logger and task messenger to this job_id
    listen_for_task_messages(job_id)

    msg: Message = Message(
        job_id, status="running", text="Starting moving target query."
    )
    msg.publish()

    _sources: List[str] = allowed_sources if sources is None else sources

    exc: Exception
    try:
        with catch_manager() as catch:
            catch.start_date = None if start_date is None else Time(start_date)
            catch.stop_date = None if stop_date is None else Time(stop_date)
            catch.uncertainty_ellipse = uncertainty_ellipse
            catch.padding = padding
            catch.query(target, job_id, sources=_sources, cached=cached)
        msg.status = TaskStatus.SUCCESS
        msg.text = "Task complete."
    except (CatchException, SBSException) as exc:  # noqa: F841
        logger.exception("catch error.")
        msg.status = TaskStatus.ERROR
        msg.text = str(exc)
    except Exception:
        logger.exception("An unexpected error occurred.")
        msg.status = TaskStatus.ERROR
        msg.text = "An unexpected error occurred.  Contact us if this problem persists."
    finally:
        msg.publish()
        stop_listening_for_task_messages(job_id)
