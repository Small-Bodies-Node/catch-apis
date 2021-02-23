"""Service provider for moving target queries."""

import enum
from uuid import UUID
from typing import Dict, List, Optional, Union

from .catch_manager import catch_manager
from .queue import JobsQueue
from .. import tasks


class QueryStatus(enum.Enum):
    UNDEFINED = 'undefined'
    SUCCESS = 'success'
    QUEUED = 'queued'
    QUEUEFULL = 'queue full'


def moving_target_query(job_id: UUID, target: str,
                        source: Optional[str] = None,
                        cached: bool = False) -> Dict[str, bool]:
    """Engueue a query or copy cached results.


    Parameters
    ----------
    target : string
        The target target.

    source : str, optional
        Search this source, or else all sources.

    cached : bool, optional
        ``True`` if it is OK to return cached results.


    Returns
    -------
    status : QueryStatus

    queue_full : bool
        ``True`` if the query queue is full.

    """

    status: QueryStatus = QueryStatus.UNDEFINED
    queue: JobsQueue = JobsQueue()
    source_keys: Union[None, List[str]] = None if source is None else [source]

    if cached:
        with catch_manager() as catch:
            if catch.is_query_cached(target, source_keys=source_keys):
                # copy cached results to the new job ID
                catch.query(target, job_id, source_keys=source_keys,
                            cached=True)
                status = QueryStatus.SUCCESS

    if status != status.SUCCESS:
        if queue.full:
            status = QueryStatus.QUEUEFULL
        else:
            queue.enqueue(tasks.catch_moving_target, job_id, target,
                          source_keys, False)
            status = QueryStatus.QUEUED

    return status, queue.full
