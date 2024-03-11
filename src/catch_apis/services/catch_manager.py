"""CATCH library interaction."""

from typing import Iterator
from contextlib import contextmanager

from catch import Catch, Config

from .database_provider import data_provider_session
from ..config.env import ENV


@contextmanager
def catch_manager(save_log: bool = True) -> Iterator[Catch]:
    """Catch library session manager."""
    with data_provider_session() as session:
        config = Config(database=session, log=ENV.CATCH_LOG_FILE, debug=ENV.DEBUG)
        with Catch.with_config(config) as catch:
            yield catch
