from uuid import UUID
from sqlalchemy import func

from catch.model import CatchQuery, Found

from ..catch_manager import Catch, catch_manager


def job_id(job_id: UUID) -> tuple[dict, list[dict]]:
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

    status: list[dict[str, str | int | None]] = []
    parameters: dict[str, str | int | float | None] = {}

    catch: Catch
    with catch_manager() as catch:
        queries: list[CatchQuery] = catch.queries_from_job_id(job_id)
        if len(queries) == 0:
            return {"message": "No jobs found with requested ID"}, []

        # count number of detections by observational data source
        counts: dict[str, int] = {}
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

        parameters["target"] = queries[0].query
        parameters["start_date"] = queries[0].start_date
        parameters["stop_date"] = queries[0].stop_date
        parameters["uncertainty_ellipse"] = queries[0].uncertainty_ellipse
        parameters["padding"] = queries[0].padding

    return parameters, status
