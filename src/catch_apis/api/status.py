"""Summary of data sources.

Exposes results from the survey_statistics database table.

"""

import uuid
from typing import Dict, Union, List, Tuple
from .. import services
from .. import __version__ as version


def sources() -> List[Dict[str, Union[str, int, None]]]:
    """Controller for returning survey database status."""

    return services.status.sources()


def job_id(job_id: str) -> Union[dict, Tuple[str, int]]:
    """Controller for returning job ID status."""

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
