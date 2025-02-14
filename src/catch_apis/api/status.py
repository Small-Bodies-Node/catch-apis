"""Summary of data sources.

Exposes results from the survey_statistics database table.

"""

from uuid import UUID
from ..services.status.sources import sources_service
from ..services.status.job_id import job_id_service
from ..services.status.updates import updates_service
from ..services.status.queue import queue_service
from ..services.status.queries import queries_service
from .. import __version__ as version


def sources_controller() -> list[dict[str, str | int | None]]:
    """Controller to return survey database status."""

    return sources_service()


def job_id_controller(job_id: str) -> dict | tuple[str, int]:
    """Controller to return job ID status."""

    try:
        _job_id: UUID = UUID(job_id, version=4)
    except ValueError:
        return "Invalid job ID", 400

    parameters, status = job_id_service(_job_id)

    return {
        "job_id": job_id,
        "version": version,
        "parameters": parameters,
        "status": status,
    }


def updates_controller() -> list[dict[str, str | int | None]]:
    """Controller to return summary of recent updates."""

    return updates_service()


def queue_controller() -> dict[str, bool | list[dict[str, str | int]]]:
    """Controller to return summary of job queue."""

    return queue_service()


def queries_controller() -> list[dict[str, str | int]]:
    """Controller to return summary of recent queries."""

    return queries_service()
