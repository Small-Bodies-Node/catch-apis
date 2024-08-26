"""Environment variables.

The values are always updated when the module is imported.

To support the testing suite, only use ``import`` on the module, do not use
``from ... import ...``.

"""

import os
import sys
from typing import Dict, Tuple, get_type_hints
import inspect
from dotenv import load_dotenv, find_dotenv

# parameters and defaults

## String properties
APP_NAME: str = "catch-apis"
TEST_DATA_PATH: str = os.path.abspath("./data/test")
DEPLOYMENT_TIER: str = "LOCAL"
DB_HOST: str = ""
DB_DIALECT: str = "postgresql"
DB_USERNAME: str = ""
DB_PASSWORD: str = ""
DB_DATABASE: str = "catch"
BASE_HREF: str = "/"
API_HOST: str = "0.0.0.0"
REDIS_HOST: str = "127.0.0.1"
REDIS_TASK_MESSAGES: str = ""
REDIS_JOBS: str = ""
CATCH_LOG_FILE: str = os.path.abspath("./logging/catch.log")
CATCH_APIS_LOG_FILE: str = os.path.abspath("./logging/catch-apis.log")

## Numeric properties
GUNICORN_WORKER_INSTANCES: int = -1
GUNICORN_FLASK_INSTANCES: int = -1
API_PORT: int = 5000
REDIS_PORT: int = 6379
REDIS_MAX_QUEUE_SIZE: int = 100
STREAM_TIMEOUT: int = 60  # seconds

## Boolean Properties
DEBUG: bool = False


def _get_parameters() -> Tuple[str, str | int | bool]:
    """Returns the configurable parameters in this module."""

    return inspect.getmembers(
        sys.modules[__name__],
        lambda member: isinstance(member, (str, int, bool)),
    )


def _update_from_dictionary(updates: Dict[str, str | int | bool]) -> None:
    """Update parameters based on the provided dictionary."""

    parameters: Tuple[str, str | int | bool] = _get_parameters()
    types = get_type_hints(sys.modules[__name__])
    for name, value in parameters:
        if name.startswith("_"):
            continue
        hint = types[name]
        value = updates.get(name, os.getenv(name))
        if value is None:
            continue
        if hint is bool and isinstance(value, str):
            value = value.lower() in ["true", "1"]
        setattr(sys.modules[__name__], name, hint(value))


def _update_from_environment(dotenv) -> None:
    """Update parameters based on the OS environment.


    Parameters
    ----------
    dotenv : bool
        Set to ``True`` to update the environment with the .env file.

    """

    if dotenv:
        load_dotenv(find_dotenv(), override=True)

    updates: Dict[str, str] = {}
    parameters: Tuple[str, (str, int, bool)] = _get_parameters()
    for name, _ in parameters:
        value: str = os.getenv(name)
        if value is not None:
            updates[name] = value
    _update_from_dictionary(updates)


def update(updates: Dict[str, str | int | bool] | None = None, dotenv=False):
    """Update environment parameters.


    Parameters
    ----------
    updates : dict, optional
        A dictionary of parameter-value updates.  These values take precedence
        over the OS environment and .env file.

    dotenv : bool, optional
        Set to ``True`` to find and update the OS environment with a .env file.

    """

    _update_from_environment(dotenv)
    if updates is not None:
        _update_from_dictionary(updates)


# always update from the environment when the module is imported
update(dotenv=True)
