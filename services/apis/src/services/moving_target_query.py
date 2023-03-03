"""Service provider for moving target queries."""

import enum
from uuid import UUID
from typing import List, Optional

from .catch_manager import catch_manager
from .queue import JobsQueue
from .. import tasks


class QueryStatus(enum.Enum):
    UNDEFINED = 'undefined'
    SUCCESS = 'success'
    QUEUED = 'queued'
    QUEUEFULL = 'queue full'


def moving_target_query(job_id: UUID, target: str,
                        sources: Optional[List[str]],
                        uncertainty_ellipse: bool,
                        padding: float, cached: bool
                        ) -> QueryStatus:
    """Enqueue a query or copy cached results.


    Parameters
    ----------
    target : string
        The target target.

    sources : list of str
        Search these sources, or, if ``None``, all sources.

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
            catch.uncertainty_ellipse = uncertainty_ellipse
            catch.padding = padding
            # if catch.is_query_cached(target, source_keys=source):
            if catch.is_query_cached(target, sources=sources):
                # copy cached results to the new job ID
                # catch.query(target, job_id, source_keys=source, cached=True)
                catch.query(target, job_id, sources=sources, cached=True)
                status = QueryStatus.SUCCESS

    if status != QueryStatus.SUCCESS:
        if queue.full:
            status = QueryStatus.QUEUEFULL
        else:
            queue.enqueue(f=tasks.catch_moving_target,
                          args=[job_id, target,
                                sources, uncertainty_ellipse, padding, False],
                          job_timeout=1200
                          )
            status = QueryStatus.QUEUED

    return status
