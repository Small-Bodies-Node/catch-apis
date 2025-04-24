# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
from time import monotonic

from sbsearch.exceptions import SBSException
from catch.exceptions import CatchException

from ...config import get_logger
from ...services.catch_manager import catch_manager
from ...services.download import DataProducts
from ...services.message import (
    Message,
    listen_for_task_messages,
    stop_listening_for_task_messages,
    TaskStatus,
)
from .package_manager import PackageManager


def package(job_id: uuid.UUID, data_products: DataProducts):
    """Package data, publish progress to message stream.


    Parameters
    ----------
    data_products : DataProducts
        Data products to package up.

    job_id : UUID
        Job identifier used to communicate with the user.


    Returns
    -------
    filenames : list of str
        Packaged data file names.

    """

    logger = get_logger()

    # subscribe the logger and task messenger to this job_id
    listen_for_task_messages(job_id)

    Message.t0 = monotonic()
    msg: Message = Message(job_id, status=TaskStatus.RUNNING, text="Packaging started")
    msg.publish()

    filenames = []
    try:
        packager = PackageManager(job_id)
        with catch_manager() as catch:
            filenames = packager.package(catch, data_products)
        msg.status = TaskStatus.SUCCESS
        msg.text = "Packaging complete"
    except (CatchException, SBSException) as exc:
        logger.exception("catch error")
        msg.status = TaskStatus.ERROR
        msg.text = str(exc)
    except Exception:
        logger.exception("An unexpected error occurred")
        msg.status = TaskStatus.ERROR
        msg.text = "An unexpected error occurred.  Contact us if the problem persists."
    finally:
        msg.publish()
        stop_listening_for_task_messages(job_id)

    return filenames
