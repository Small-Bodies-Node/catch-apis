"""CATCH library interaction."""

from typing import Iterator
from contextlib import contextmanager

from catch import Catch, Config

from catch_apis.config.env import ENV
from .database_provider import data_provider_session


@contextmanager
def catch_manager(save_log: bool = True) -> Iterator[Catch]:
    """Catch library session manager."""

    with data_provider_session() as session:
        config = Config(database=session, log=ENV.CATCH_LOG_FILE, debug=ENV.DEBUG)
        with Catch.with_config(config) as catch:
            yield catch
