import uuid

from ..services.caught import caught_service
from ..services.status.job_id import job_id_service
from .. import __version__ as version


def caught_controller(job_id: str) -> dict | tuple[str, int]:
    """Controller for returning caught data."""

    try:
        _job_id: uuid.UUID = uuid.UUID(job_id, version=4)
    except ValueError:
        return "Invalid job ID", 400

    parameters, status = job_id_service(_job_id)
    data = caught_service(_job_id)
    return {
        "parameters": parameters,
        "status": status,
        "count": len(data),
        "job_id": _job_id.hex,
        "version": version,
        "data": data,
    }
