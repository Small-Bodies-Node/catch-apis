import uuid
import logging

from sbsearch.exceptions import SBSException
from catch.exceptions import CatchException

from ..services.catch_manager import catch_manager
from ..services.message import (Message, listen_for_task_messages,
                                stop_listening_for_task_messages,
                                TaskStatus)
from ..config.logging import get_logger


def catch_moving_target(job_id: uuid.UUID, target: str, source_keys: str,
                        uncertainty_ellipse: bool, padding: float,
                        cached: bool) -> None:
    """Search for target in CATCH surveys.


    Parameters
    ----------
    job_id : uuid.UUID
        Unique ID for job.

    target : string
        Target target.

    source_keys : string or None
        Name of observation sources to search or ``None`` to search all
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

    exc: Exception
    try:
        with catch_manager() as catch:
            catch.uncertainty_ellipse = uncertainty_ellipse
            catch.padding = padding
            catch.query(target, job_id, source_keys=source_keys,
                        cached=cached)

        msg.status = TaskStatus.SUCCESS
        msg.text = 'Task complete.'
    except (CatchException, SBSException) as exc:
        logger.exception("catch error.")
        msg.status = TaskStatus.ERROR
        msg.text = str(exc)
    except:
        logger.exception("An unexpected error occurred.")
        msg.status = TaskStatus.ERROR
        msg.text = 'An unexpected error occurred.  Contact us if this problem persists.'
    finally:
        msg.publish()
        stop_listening_for_task_messages(job_id)
