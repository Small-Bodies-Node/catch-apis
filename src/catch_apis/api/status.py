"""Summary of data sources.

Exposes results from the survey_statistics database table.

"""

from uuid import UUID
from astropy.time import Time
from .. import services
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
    status : dict
        - depth: number of jobs allowed in the queue
        - full: True if the queue is full
        - jobs: list of job summaries
            - prefix: job ID prefix
            - position: queue position
            - enqueued_at: time the query was added to the queue
            - status: the job's status

    """

    return services.status.queue()


def queries() -> list[dict[str, str | int]]:
    """Controller to return summary of recent queries."""

    return services.status.queries()
