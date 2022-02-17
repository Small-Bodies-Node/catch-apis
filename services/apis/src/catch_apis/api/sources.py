"""Summary of data sources.

Exposes results from the survey_statistics database table.

"""

from typing import Dict, Union, List
from .. import services


def sources() -> List[Dict[str, Union[str, int, None]]]:
    """Controller for returning caught data."""

    return services.sources()
