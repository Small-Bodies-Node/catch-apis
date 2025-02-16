# Licensed with the 3-clause BSD license.  See LICENSE for details.

import pytest
from importlib import reload
from urllib.parse import urlparse
from collections import defaultdict

import testing.postgresql
from starlette.testclient import TestClient
import numpy as np
from astropy.time import Time

from catch.catch import Catch
from catch.config import Config
from catch.model import NEATPalomarTricam
from catch import stats

# only import env here, defer any other imports until after the environment is
# updated
from catch_apis.config.env import ENV

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
        "GUNICORN_FLASK_INSTANCES": 1,
        "CATCH_QUEUE_WORKER_INSTANCES": 1,
        "API_PORT": 5000,
        "REDIS_PORT": 6379,
        "REDIS_JOBS_MAX_QUEUE_SIZE": 5,
        "REDIS_TASK_MESSAGES_MAX_QUEUE_SIZE": 1000,
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
    count = 0
    for iteration in range(4):
        for dec in np.arange(-10, 21, 5):
            for ra in np.arange(-10, 21, 5):
                count += 1
                product_id = f"urn:nasa:pds:gbo.ast.neat.survey:data_tricam:p20011126_obsdata_{count}"
                _fov = fov + np.array([[ra], [dec]])
                obs = NEATPalomarTricam(
                    mjd_start=mjd_start,
                    mjd_stop=mjd_start + EXPTIME,
                    product_id=product_id,
                    mjd_added=Time.now().mjd,
                )
                obs.set_fov(*_fov)
                observations.append(obs)

                mjd_start += EXPTIME + SLEWTIME

    config = Config(database=postgresql.url(), log="/dev/null", debug=True)
    with Catch.with_config(config) as catch:
        catch.add_observations(observations)
        stats.update_statistics(catch)


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


class MockedJob:
    def __init__(self, f, args, position):
        self.f = f
        self.args = args
        self.position = position
        self.enqueued_at = Time.now().iso

    def get_position(self):
        return self.position

    def get_status(self):
        return "queued"


class MockedJobsQueue:
    def __init__(self, *args, **kwargs):
        self.jobs = []

    @property
    def full(self):
        return len(self.jobs) >= ENV.REDIS_JOBS_MAX_QUEUE_SIZE

    def enqueue(self, **kwargs):
        self.jobs.append(MockedJob(kwargs["f"], kwargs["args"], len(self.jobs)))


class MockedRedisConnection:
    def __init__(self, *args, **kwargs):
        self.items = defaultdict(list)
        self.last = None

    def xadd(self, name, data, **kwargs):
        self.items[name].append(data)

    def xread(self, streams, **kwargs):
        # very sloppy, but getting accurate and precise is not important for our
        # testing
        name = list(streams.keys())[0]
        if len(self.items[name]) == 0:
            return []
        return [[b"0", [(b"1", self.items[name].pop(0))]]]

    def llen(self, name, *args, **kwargs):
        return len(self.items[name])

    def lrange(self, key, start, end):
        for i in range(start, end + 1):
            if i < len(self.items[key]):
                yield self.items[key]
                continue
            break


@pytest.fixture
def mock_redis(monkeypatch):
    """Mocked classes to avoid any interaction with redis."""

    import catch_apis.services.catch
    import catch_apis.services.message
    import catch_apis.services.status.queue
    import catch_apis.services.queue

    jobs_queue = MockedJobsQueue()

    monkeypatch.setattr(catch_apis.api.catch, "JobsQueue", lambda: jobs_queue)
    monkeypatch.setattr(
        catch_apis.services.status.queue, "JobsQueue", lambda: jobs_queue
    )
    monkeypatch.setattr(catch_apis.services.catch, "JobsQueue", lambda: jobs_queue)

    monkeypatch.setattr(
        catch_apis.services.message, "RedisConnection", MockedRedisConnection
    )


@pytest.fixture
def mock_flask_request(monkeypatch):
    """Mocked flask.request"""

    import catch_apis.api.catch

    class Request:
        url_root = "http://testserver/"

    monkeypatch.setattr(catch_apis.api.catch, "request", Request)


@pytest.fixture
def mock_messages(monkeypatch):
    import catch_apis.services.message
    import catch_apis.services.stream

    redis_connection = MockedRedisConnection()

    monkeypatch.setattr(
        catch_apis.services.message, "RedisConnection", lambda: redis_connection
    )
    monkeypatch.setattr(
        catch_apis.services.stream, "RedisConnection", lambda: redis_connection
    )
