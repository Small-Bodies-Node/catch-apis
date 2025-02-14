from catch import stats
from ..catch_manager import Catch, catch_manager
from ...config import allowed_sources


def updates_service() -> list[dict[str, str | int | None]]:
    "Get a summary of data recently added to the CATCH database."

    with catch_manager() as catch:
        data = stats.recently_added_observations(catch, allowed_sources)

    return data
