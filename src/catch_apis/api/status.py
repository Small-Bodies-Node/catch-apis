"""Summary of data sources.

Exposes results from the survey_statistics database table.

"""

import uuid
from .. import services
from .. import __version__ as version


def sources() -> list[dict[str, str | int | None]]:
    """Controller to return survey database status."""

    return services.status.sources()


def job_id(job_id: str) -> dict | tuple[str, int]:
    """Controller to return job ID status."""

    try:
        _job_id: uuid.UUID = uuid.UUID(job_id, version=4)
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
