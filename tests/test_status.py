# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
from starlette.testclient import TestClient
from astropy.time import Time

from catch_apis.api.catch import catch_controller
from catch_apis.tasks.catch import catch_task
from catch_apis.config.env import ENV
from . import (  # noqa: F401
    fixture_test_client,
    mock_flask_request,
    mock_redis,
    MockedJobsQueue,
)


def test_status_sources(test_client: TestClient):
    response = test_client.get("/status/sources")
    response.raise_for_status()
    results = response.json()

    (test_sky_survey,) = [row for row in results if row["source"] == "test_sky_survey"]
    assert test_sky_survey["count"] == 49 * 4
    assert test_sky_survey["start_date"].startswith("2012-03-14")
    assert test_sky_survey["stop_date"].startswith("2012-03-14")
    assert test_sky_survey["nights"] == 1


def test_status_job_id(test_client: TestClient, mock_redis):  # noqa: F811
    job_id = uuid.uuid4()
    catch_task(job_id, "65P", ["test_sky_survey"], None, None, False, 0, True)

    response = test_client.get(f"/status/{job_id.hex}")
    response.raise_for_status()
    results = response.json()
    assert results["job_id"] == job_id.hex
    expected = {
        "padding": 0,
        "start_date": None,
        "stop_date": None,
        "target": "65P",
        "sources": ["test_sky_survey"],
        "uncertainty_ellipse": False,
    }
    for k, v in expected.items():
        assert results["parameters"][k] == v

    expected = {
        "count": 0,
        "source": "test_sky_survey",
        "source_name": "Test Sky Survey",
        "status": "finished",
    }
    for k, v in expected.items():
        assert results["status"][0][k] == v

    # date should be parsable by Time
    Time(results["status"][0]["date"])

    assert results["status"][0]["execution_time"] > 0

    # test invalid job id
    response = test_client.get("/status/invalid_job_id")
    assert response.status_code == 400


def test_updates(test_client: TestClient):
    response = test_client.get("/status/updates")
    response.raise_for_status()
    results = response.json()

    assert len(results) == 3

    # they should all be the same except for days
    for i in range(3):
        assert results[i]["count"] == 196
        assert results[i]["source"] == "test_sky_survey"
        assert results[i]["source_name"] == "Test Sky Survey"
        assert results[i]["start_date"] == "2012-03-14 00:00:00.000"
        assert results[i]["stop_date"] == "2012-03-14 02:00:45.000"

    assert [result["days"] for result in results] == [1, 7, 30]


def test_queue(
    test_client: TestClient, mock_redis, mock_flask_request, monkeypatch  # noqa: F811
):
    controller_responses = []
    for i in range(3):
        controller_responses.append(catch_controller("65P", cached=False))

    response = test_client.get("/status/queue")
    response.raise_for_status()
    results = response.json()

    assert results["depth"] == ENV.REDIS_JOBS_MAX_QUEUE_SIZE
    assert not results["full"]
    assert len(results["jobs"]) == 3
    assert results["jobs"][0]["prefix"] == controller_responses[0]["job_id"][:8]
    assert results["jobs"][0]["position"] == 0
    Time(results["jobs"][0]["enqueued_at"])
    assert results["jobs"][0]["status"] == "queued"


def test_queries(test_client: TestClient):
    response = test_client.get("/status/queries")
    response.raise_for_status()
    results = response.json()
    assert len(results) == 3
    for i, d in enumerate([1, 7, 30]):
        assert results[i]["days"] == d
        assert results[i]["cached"] == 0
        assert results[i]["errored"] == 0
        assert results[i]["finished"] == 0
        assert results[i]["in_progress"] == 0
        assert results[i]["jobs"] == 0
