"""   """
import uuid
import logging
from typing import Any, Dict, List, Tuple, Union
from .. import services
from ..config.logging import get_logger


def caught(job_id: str) -> Union[dict, Tuple[str, int]]:
    """Controller for returning caught data."""

    from ..api.app import version  # avoid circular import

    logger: logging.Logger = get_logger()
    try:
        _job_id: uuid.UUID = uuid.UUID(job_id, version=4)
    except ValueError:
        return "Invalid job ID", 400

    data: List[Dict[str, Any]] = services.caught(_job_id)
    return {
        "count": len(data),
        "job_id": _job_id.hex,
        "version": version,
        "data": data,
    }
