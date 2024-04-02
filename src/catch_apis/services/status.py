from uuid import UUID
from typing import Dict, Union, List, Tuple
from sqlalchemy import func

from catch.model import SurveyStats, CatchQuery, Found

from .catch_manager import Catch, catch_manager
from .caught import caught
from ..config import allowed_sources


def sources() -> List[Dict[str, Union[str, int, None]]]:
    """Get source summary statistics from CATCH database."""

    data: List[Dict[str, Union[str, int, None]]] = []

    catch: Catch
    with catch_manager() as catch:
        for summary in catch.db.session.query(SurveyStats).all():
            # keep this limited to the allowed_sources, and do not include the
            # "All" data summary since it can have development or deprecated
            # data sources
            if summary.source in allowed_sources:
                data.append(
                    {
                        "source": summary.source,
                        "source_name": summary.name,
                        "count": summary.count,
                        "start_date": summary.start_date,
                        "stop_date": summary.stop_date,
                        "updated": summary.updated,
                    }
                )
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
        queries: List[CatchQuery] = catch.queries_from_job_id(job_id)

        # count number of detections by observational data source
        counts: Dict[str, int] = {}
        counts.update(
            catch.db.session.query(CatchQuery.source, func.count(CatchQuery.source))
            .filter(CatchQuery.job_id == job_id.hex)
            .join(Found)
            .group_by(CatchQuery.source)
            .all()
        )

        query: CatchQuery
        for query in queries:
            source: str = query.source
            status.append(
                {
                    "source": source,
                    "source_name": catch.sources[source].__data_source_name__,
                    "date": query.date,
                    "status": query.status,
                    "execution_time": query.execution_time,
                    "count": counts.get(source, 0),
                }
            )

        parameters["target"] = query.query
        parameters["start_date"] = query.start_date
        parameters["stop_date"] = query.stop_date
        parameters["uncertainty_ellipse"] = query.uncertainty_ellipse
        parameters["padding"] = query.padding

    return parameters, status
