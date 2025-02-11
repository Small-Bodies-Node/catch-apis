# Licensed with the 3-clause BSD license.  See LICENSE for details.

import pytest
from importlib import reload
from urllib.parse import urlparse

import testing.postgresql
from sqlalchemy import BigInteger, Column, String, ForeignKey
from starlette.testclient import TestClient
import numpy as np

from catch.catch import Catch
from catch.config import Config
from catch.model import Observation
from catch import stats

# only import env here, defer any other imports until after the environment is
# updated
from catch_apis.config.env import ENV


# testing defaults
ENV.update(
    {
        "DEPLOYMENT_TIER": "TEST",
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
        "REDIS_JOBS_MAX_QUEUE_SIZE": 100,
        "REDIS_TASK_MESSAGES_MAX_QUEUE_SIZE": 1000,
        "STREAM_TIMEOUT": 60,
        "DEBUG": False,
    }
)

# test survey parameters
SURVEY_START: float = 56000.0
EXPTIME: float = 30 / 86400
SLEWTIME: float = 7 / 86400


class SkySurvey(Observation):
    """Test survey data model."""

    __tablename__: str = "test_sky_survey"
    __data_source_name__: str = "Test Sky Survey"
    __obscode__: str = "644"  # MPC observatory code
    __field_prefix__: str = "tss"
    __night_offset__: float = -0.33

    source_id = Column(BigInteger, primary_key=True)
    observation_id = Column(
        BigInteger,
        ForeignKey(
            "observation.observation_id", onupdate="CASCADE", ondelete="CASCADE"
        ),
        nullable=False,
        index=True,
    )
    product_id = Column(
        String(100), doc="Archive product id", unique=True, index=True, nullable=False
    )

    __mapper_args__ = {"polymorphic_identity": "test_sky_survey"}

    @property
    def archive_url(self):
        product_id = self.product_id[self.product_id.rindex(":") + 1 :]
        return f"http://testserver/test/data/{product_id}.fits"

    @property
    def label_url(self):
        return self.archive_url[:-4] + "xml"

    def cutout_url(self, ra, dec, size=0.1, format="fits"):
        url = self.archive_url
        if url is None:
            return None

        if format == "jpeg":
            url = url[:-4]
        elif format != "fits":
            raise NotImplementedError
        return f"{url}?ra={ra}&dec={dec}&size={size}"

    def preview_url(self, ra, dec, format="jpeg"):
        return self.cutout_url(ra, dec, format)


def dummy_surveys(postgresql):
    mjd_start = SURVEY_START
    fov = np.array(((-0.5, 0.5, 0.5, -0.5), (-0.5, -0.5, 0.5, 0.5))) * 5
    observations = []
    count = 0
    for iteration in range(4):
        for dec in np.arange(-10, 21, 5):
            for ra in np.arange(-10, 21, 5):
                count += 1
                product_id = f"urn:nasa:pds:gbo.ast.tss:data:{count}"
                _fov = fov + np.array([[ra], [dec]])
                obs = SkySurvey(
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
        stats.update_statistics(catch)


Postgresql = testing.postgresql.PostgresqlFactory(
    cache_initialized_db=True,
    on_initialized=dummy_surveys,
)


@pytest.fixture(name="test_client")
def fixture_test_client():
    # deferred imports so that the testing environment is up to date
    import catch_apis.config

    catch_apis.config.allowed_sources.append("test_sky_survey")

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
