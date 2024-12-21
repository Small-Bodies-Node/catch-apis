from catch.model import SurveyStats

from ..catch_manager import Catch, catch_manager
from ...config import allowed_sources


def sources() -> list[dict[str, str | int | None]]:
    """Get source summary statistics from CATCH database."""

    data: list[dict[str, str | int | None]] = []

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
