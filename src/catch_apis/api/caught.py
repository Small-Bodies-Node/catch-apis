
import os
import uuid
import logging
from typing import Any, Dict, List, Tuple, Union
from .. import services
from ..logging import get_logger


def caught(job_id: str) -> Union[dict, Tuple[dict, int]]:
    """Controller for returning caught data."""

    logger: logging.Logger = get_logger()
    try:
        job_id: uuid.UUID = uuid.UUID(job_id, version=4)
    except ValueError:
        return 'Invalid job ID', 400

    data: List[Dict[str, Any]] = services.caught(job_id)
    return {
        "count": len(data),
        "job_id": job_id.hex,
        "data": data
    }
