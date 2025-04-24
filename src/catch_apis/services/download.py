# Licensed with the 3-clause BSD license.  See LICENSE for details.

from uuid import UUID

from .queue import JobsQueue
from ..tasks import download
from ..config import PackagingStatus
from ..model import DataProducts


def package(job_id: UUID, data_products: DataProducts) -> PackagingStatus:
    """Enqueue a job to package data for downloading.


    Parameters
    ----------
    job_id : `UUID`
        Unique job identifier.

    data_products: DataProducts
        Data to download.

    """

    status: PackagingStatus = PackagingStatus.UNDEFINED
    queue: JobsQueue = JobsQueue()

    if queue.full:
        status = PackagingStatus.QUEUEFULL
    else:
        queue.enqueue(
            f=download.package,
            args=[
                job_id,
                data_products,
            ],
            job_timeout=1200,
        )
        status = PackagingStatus.QUEUED

    return status
