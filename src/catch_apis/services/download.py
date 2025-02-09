# Licensed with the 3-clause BSD license.  See LICENSE for details.

from uuid import UUID

from .queue import JobsQueue
from .. import tasks
from ..config import PackagingStatus


class DataProducts:
    """Specifications for data to download.


    Parameters
    ----------
    images : list of dict
        List of image specifications:
            - observation_id: (required)
            - cutout: (optional)
                - ra: right ascension, degrees
                - dec: declination, degrees
                - size: cutout size, degrees
                - format: cutout format

    previews : bool
        Also download preview (JPEG) images.

    """

    def __init__(self, images: list[dict], previews: bool):
        self.images = images
        self.previews = previews

        # sort image requests into a list by observation ID
        self.images_by_id: dict[int, dict] = {
            image["observation_id"]: image for image in self.images
        }

    @property
    def observation_ids(self):
        return list(self.images_by_id.keys())

    def cutout_spec(self, observation_id: int) -> dict[str, float] | None:
        """Get the user's requested cutout parameters.


        Parameters
        ----------
        observation_id : int
            The observation ID in question.


        Returns
        -------
        spec : dict or None
            The specifications (ra, dec, size) or None, if no cutout requested.

        """

        return self.images_by_id.get(observation_id, {}).get("cutout")


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
            f=tasks.package,
            args=[
                job_id,
                data_products,
            ],
            job_timeout=1200,
        )
        status = PackagingStatus.QUEUED

    return status
