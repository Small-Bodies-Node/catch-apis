# Licensed with the 3-clause BSD license.  See LICENSE for details.

import pytest
from importlib import reload
from urllib.parse import urlparse

import testing.postgresql
from starlette.testclient import TestClient
import numpy as np

from catch.catch import Catch
from catch.config import Config
from catch.model import NEATPalomarTricam

# only import env here, defer any other imports until after the environment is
# updated
import catch_apis.config.env as ENV

# testing defaults
ENV.update(
    {
        "DEPLOYMENT_TIER": "LOCAL",
        "DB_HOST": "",
        "DB_DIALECT": "postgresql",
        "DB_USERNAME": "",
        "DB_PASSWORD": "",
        "DB_DATABASE": "catch_test",
        "BASE_HREF": "/",
        "API_HOST": "localhost",
        "REDIS_HOST": "redis",
        "REDIS_TASK_MESSAGES": "TEST_TASK_MESSAGES",
        "REDIS_JOBS": "TEST_JOBS",
        "CATCH_LOG_FILE": "./logging/catch_test.log",
        "CATCH_APIS_LOG_FILE": "./logging/catch_apis_test.log",
        "GUNICORN_WORKER_INSTANCES": 1,
        "GUNICORN_FLASK_INSTANCES": 1,
        "API_PORT": 5000,
        "REDIS_PORT": 6379,
        "REDIS_MAX_QUEUE_SIZE": 100,
        "STREAM_TIMEOUT": 60,
        "DEBUG": False,
    }
)

# test survey parameters
SURVEY_START: float = 56000.0
EXPTIME: float = 30 / 86400
SLEWTIME: float = 7 / 86400


def dummy_surveys(postgresql):
    mjd_start = SURVEY_START
    fov = np.array(((-0.5, 0.5, 0.5, -0.5), (-0.5, -0.5, 0.5, 0.5))) * 5
    observations = []
    product_id = 0
    for iteration in range(4):
        for dec in np.arange(-10, 21, 5):
            for ra in np.arange(-10, 21, 5):
                product_id += 1
                _fov = fov + np.array([[ra], [dec]])
                obs = NEATPalomarTricam(
                    mjd_start=mjd_start,
                    mjd_stop=mjd_start + EXPTIME,
                    product_id=product_id,
                )
                obs.set_fov(*_fov)
                observations.append(obs)

                mjd_start += EXPTIME + SLEWTIME

    config = Config(database=postgresql.url(), log="/dev/null", debug=True)
    with Catch.with_config(config) as catch:
        catch.add_observations(observations)
        catch.update_statistics()


Postgresql = testing.postgresql.PostgresqlFactory(
    cache_initialized_db=True,
    on_initialized=dummy_surveys,
)


@pytest.fixture(name="test_client")
def fixture_test_client():
    # deferred imports so that the testing environment is up to date
    import catch_apis.app
    import catch_apis.services.database_provider

    with Postgresql() as postgresql:
        url = urlparse(postgresql.url())
        ENV.update(
            {
                "DB_HOST": ":".join([url.hostname, str(url.port)]),
                "DB_USERNAME": url.username,
                "DB_PASSWORD": "",
                "DB_DATABASE": url.path.strip("/"),
            }
        )
        reload(catch_apis.services.database_provider)

        yield TestClient(catch_apis.app.app)
