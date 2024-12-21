from sqlalchemy import func
from astropy.time import Time
from catch.model import Observation
from ..catch_manager import Catch, catch_manager
from ...config import allowed_sources
from ...config.logging import get_logger


def updates() -> list[dict[str, str | int | None]]:
    "Get a summary of data recently added to the CATCH database."

    data: list[dict[str, str | int | None]]
    catch: Catch
    with catch_manager() as catch:
        data = catch.status_updates()
    return data
