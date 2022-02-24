from typing import Dict, Union, List

from catch.model import SurveyStats

from .catch_manager import Catch, catch_manager
from .. import tasks


def sources() -> List[Dict[str, Union[str, int, None]]]:
    """Get source summary statistics from CATCH database."""

    data: List[Dict[str, Union[str, int, None]]] = []

    catch: Catch
    with catch_manager() as catch:
        for summary in catch.db.session.query(SurveyStats).all():
            if summary.source in tasks.QUERY_SOURCES:
                data.append({
                    'source': summary.source,
                    'source_name': summary.name,
                    'count': summary.count,
                    'start_date': summary.start_date,
                    'stop_date': summary.stop_date,
                    'updated': summary.updated,
                })
    return data
