"""Service provider for moving target queries."""

from uuid import UUID
from typing import List, Union

from astropy.time import Time

from .catch_manager import catch_manager
from .queue import JobsQueue
from ..tasks.catch import catch_task
from ..config import QueryStatus


def catch_service(
    job_id: UUID,
    target: str,
    sources: List[str],
    start_date: Union[Time, None],
    stop_date: Union[Time, None],
    uncertainty_ellipse: bool,
    padding: float,
    cached: bool,
) -> QueryStatus:
    """Enqueue a query or copy cached results.


    Parameters
    ----------
    job_id : `UUID`
        Unique job identifier.

    target : string
        The target target.

    sources : list of str
        Search these sources.

    start_date : Time or None
        Search after this date/time.

    stop_date : Time or None
        Search after this date/time.

    uncertainty_ellipse : bool
        Search using the ephemeris uncertainty ellipse.

    padding : bool
        Additional padding around the ephemeris search region, arcmin.

    cached : bool
        ``True`` if it is OK to return cached results.


    Returns
    -------
    status : QueryStatus

    """

    status = QueryStatus.UNDEFINED
    queue = JobsQueue()

    queue_sources = []  # sources to search in detail
    cache_sources = []  # sources to copy cached results
    if cached:
        # only check the cache if the user requested it
        with catch_manager() as catch:
            catch.start_date = start_date
            catch.stop_date = stop_date
            catch.uncertainty_ellipse = uncertainty_ellipse
            catch.padding = padding

            for source in sources:
                if catch.is_query_cached(target, sources=[source]):
                    # copy cached results to the new job ID
                    cache_sources.append(source)
                else:
                    queue_sources.append(source)
    else:
        # user did not request cached results, search all sources
        queue_sources = sources

    if len(queue_sources) == 0:
        status = QueryStatus.SUCCESS
    else:
        if queue.full:
            status = QueryStatus.QUEUEFULL
        else:
            # can parallelize search here; when this was tested on 3.0.0.dev4,
            # the message stream got several copies of the task messages
            queue.enqueue(
                f=catch_task,
                args=[
                    job_id,
                    target,
                    queue_sources,
                    start_date,
                    stop_date,
                    uncertainty_ellipse,
                    padding,
                    False,
                ],
                job_timeout=1200,
            )
            status = QueryStatus.QUEUED

    # copy cached data as needed
    if len(cache_sources) > 0:
        with catch_manager() as catch:
            catch.query(target, job_id, sources=cache_sources, cached=True)

    return status
