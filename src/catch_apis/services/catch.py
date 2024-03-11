"""Service provider for moving target queries."""

from uuid import UUID
from typing import List, Union

from astropy.time import Time

from .catch_manager import catch_manager
from .queue import JobsQueue
from .. import tasks
from ..config import QueryStatus


def catch(
    job_id: UUID,
    target: str,
    sources: Union[List[str], None],
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
        Search these sources, or, if ``None``, all sources.

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

    status: QueryStatus = QueryStatus.UNDEFINED
    queue: JobsQueue = JobsQueue()

    if cached:
        with catch_manager() as catch:
            catch.start_date = start_date
            catch.stop_date = stop_date
            catch.uncertainty_ellipse = uncertainty_ellipse
            catch.padding = padding
            if catch.is_query_cached(target, sources=sources):
                # copy cached results to the new job ID
                catch.query(target, job_id, sources=sources, cached=True)
                status = QueryStatus.SUCCESS

    if status != QueryStatus.SUCCESS:
        if queue.full:
            status = QueryStatus.QUEUEFULL
        else:
            queue.enqueue(
                f=tasks.catch,
                args=[
                    job_id,
                    target,
                    sources,
                    start_date,
                    stop_date,
                    uncertainty_ellipse,
                    padding,
                    False,
                ],
                job_timeout=1200,
            )
            status = QueryStatus.QUEUED

    return status
