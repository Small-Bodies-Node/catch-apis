"""Summary of data sources.

Exposes results from the survey_statistics database table.

"""

from uuid import UUID
from astropy.time import Time
from ..config.env import ENV
from .. import services
from ..services.queue import JobsQueue
from .. import __version__ as version


def sources() -> list[dict[str, str | int | None]]:
    """Controller to return survey database status."""

    return services.status.sources()


def job_id(job_id: str) -> dict | tuple[str, int]:
    """Controller to return job ID status."""

    try:
        _job_id: UUID = UUID(job_id, version=4)
    except ValueError:
        return "Invalid job ID", 400

    parameters, status = services.status.job_id(_job_id)

    return {
        "job_id": job_id,
        "version": version,
        "parameters": parameters,
        "status": status,
    }


def updates() -> list[dict[str, str | int | None]]:
    """Controller to return summary of recent updates."""

    return services.status.updates()


def queue() -> dict[str, bool | list[dict[str, str | int]]]:
    """Controller to return summary of job queue.


    Returns
    -------
    full : bool
        True if the queue is full.

    jobs : list of dict
        A list of jobs in the queue.

    """

    jobs: list[dict[str, str | int]] = []
    q = JobsQueue()
    for job in q.jobs:
        catch_job_id: UUID = job.args[0]

        jobs.append(
            {
                "prefix": catch_job_id.hex[:8],
                "position": job.get_position(),
                "enqueued_at": Time(job.enqueued_at).iso,
                "status": job.get_status(),
            }
        )

    return {"depth": ENV.REDIS_JOBS_MAX_QUEUE_SIZE, "full": q.full, "jobs": jobs}


def queries() -> list[dict[str, str | int]]:
    """Controller to return summary of recent queries."""

    return services.status.queries()
