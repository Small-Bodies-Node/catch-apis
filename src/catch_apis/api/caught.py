import uuid
from typing import Any, Dict, List, Tuple, Union

from .. import services
from .. import __version__ as version


def caught(job_id: str) -> Union[dict, Tuple[str, int]]:
    """Controller for returning caught data."""

    try:
        _job_id: uuid.UUID = uuid.UUID(job_id, version=4)
    except ValueError:
        return "Invalid job ID", 400

    parameters, status = services.status.job_id(_job_id)
    data: List[Dict[str, Any]] = services.caught(_job_id)
    return {
        "parameters": parameters,
        "status": status,
        "count": len(data),
        "job_id": _job_id.hex,
        "version": version,
        "data": data,
    }
