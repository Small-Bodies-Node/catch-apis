from catch import stats
from ..catch_manager import Catch, catch_manager
from ...config import allowed_sources


def queries_service() -> list[dict[str, str | int | None]]:
    "Get a summary of recent queries from the CATCH database."

    data: list[dict[str, str | int | None]]
    catch: Catch
    with catch_manager() as catch:
        data = stats.recent_queries(catch, allowed_sources)
    return data
