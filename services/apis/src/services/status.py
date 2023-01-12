from uuid import UUID
from collections import defaultdict
from typing import Dict, Union, List, Tuple

from catch.model import SurveyStats

from .catch_manager import Catch, catch_manager
from .caught import caught
from .. import tasks


def sources() -> List[Dict[str, Union[str, int, None]]]:
    """Get source summary statistics from CATCH database."""

    data: List[Dict[str, Union[str, int, None]]] = []

    catch: Catch
    with catch_manager() as catch:
        for summary in catch.db.session.query(SurveyStats).all():
            if summary.source in tasks.QUERY_SOURCES_ALLOWED:
                data.append({
                    'source': summary.source,
                    'source_name': summary.name,
                    'count': summary.count,
                    'start_date': summary.start_date,
                    'stop_date': summary.stop_date,
                    'updated': summary.updated,
                })
    return data


def job_id(job_id: UUID) -> Tuple[dict, List[dict]]:
    """Return summary of previous query by job_id.


    Parameters
    ----------
    job_id : uuid.UUID
        Unique job id for the search.


    Return
    ------
    query : dict
        The query parameters.

    status : list of dict
        The query status.

    """

    status: List[Dict[str, Union[str, int, None]]] = []
    parameters: Dict[str, Union[str, int, float, None]] = {}

    catch: Catch
    with catch_manager() as catch:
        # count number of detections by observational data source
        n_caught: Dict[str, int] = defaultdict(int)
        for row in caught(job_id):
            n_caught[row['source']] += 1

        for query in catch.queries_from_job_id(job_id):
            source: str = query.source
            status.append({
                'source': source,
                'source_name': catch.sources[source].__data_source_name__,
                'date': query.date,
                'status': query.status,
                'execution_time': query.execution_time,
                'count': n_caught.get(source)
            })

        parameters['target'] = query.query
        parameters['uncertainty_ellipse'] = query.uncertainty_ellipse
        parameters['padding'] = query.padding

    return parameters, status
