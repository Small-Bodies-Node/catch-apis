# Licensed with the 3-clause BSD license.  See LICENSE for details.

import pytest
from typing import Generator
from importlib import reload
from unittest.mock import patch
from urllib.parse import urlparse

import testing.postgresql
from starlette.testclient import TestClient
import numpy as np

from catch.catch import Catch
from catch.config import Config
from catch.model import NEATPalomarTricam
from catch_apis.config.env import ENV

# testing defaults
ENV.DEPLOYMENT_TIER = "LOCAL"
ENV.DB_HOST = ""
ENV.DB_DIALECT = "postgresql"
ENV.DB_USERNAME = ""
ENV.DB_PASSWORD = ""
ENV.DB_DATABASE = "catch_test"
ENV.BASE_HREF = "/"
ENV.API_HOST = "localhost"
ENV.REDIS_HOST = "redis"
ENV.REDIS_TASK_MESSAGES = "TEST_TASK_MESSAGES"
ENV.REDIS_JOBS = "TEST_JOBS"
ENV.CATCH_LOG_FILE = "./logging/catch_test.log"
ENV.CATCH_APIS_LOG_FILE = "./logging/catch_apis_test.log"
ENV.GUNICORN_WORKER_INSTANCES = 1
ENV.GUNICORN_FLASK_INSTANCES = 1
ENV.API_PORT = 5000
ENV.REDIS_PORT = 6379
ENV.REDIS_MAX_QUEUE_SIZE = 100
ENV.STREAM_TIMEOUT = 60
ENV.DEBUG = False

# test survey parameters
SURVEY_START = 56000.0
EXPTIME = 30 / 86400
SLEWTIME = 7 / 86400


def dummy_surveys(postgresql):
    mjd_start = SURVEY_START
    fov = np.array(((-0.5, 0.5, 0.5, -0.5), (-0.5, -0.5, 0.5, 0.5))) * 5
    observations = []
    product_id = 0
    for iteration in range(4):
        for dec in np.arange(-10, 21, 5):
            for ra in np.linspace(-10, 21, 5):
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
    cache_initialized_db=True, on_initialized=dummy_surveys
)


# @pytest.fixture(name="catch")
# def fixture_catch():
#     with Postgresql() as postgresql:
#         config = Config(database=postgresql.url(), log="/dev/null", debug=True)
#         with Catch.with_config(config) as catch:
#             print(config)
#             print(ENV)
#             yield catch


@pytest.fixture()
def test_client() -> Generator[TestClient, None, None]:
    with Postgresql() as postgresql:
        url = urlparse(postgresql.url())
        ENV.DB_HOST = ":".join([url.hostname, str(url.port)])
        ENV.DB_USERNAME = url.username
        ENV.DB_PASSWORD = ""
        ENV.DB_DATABASE = url.path.strip("/")

        with patch.dict("catch_apis.config.env.__dict__", {"ENV": ENV}):
            import catch_apis.app

            reload(catch_apis.app)
            yield catch_apis.app.app.test_client()
