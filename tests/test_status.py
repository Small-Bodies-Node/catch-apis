# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
from starlette.testclient import TestClient
from astropy.time import Time
from catch_apis.tasks.catch import catch_task
from . import fixture_test_client, mock_redis, mock_flask_request


def test_status_sources(test_client: TestClient):
    response = test_client.get("/status/sources")
    response.raise_for_status()
    results = response.json()

    (neat_palomar_tricam,) = [
        row for row in results if row["source"] == "neat_palomar_tricam"
    ]
    assert neat_palomar_tricam["count"] == 49 * 4
    assert neat_palomar_tricam["start_date"].startswith("2012-03-14")
    assert neat_palomar_tricam["stop_date"].startswith("2012-03-14")
    assert neat_palomar_tricam["nights"] == 1


def test_status_job_id(
    test_client: TestClient, mock_redis, mock_flask_request, monkeypatch
):
    job_id = uuid.uuid4()
    catch_task(job_id, "65P", ["neat_palomar_tricam"], None, None, False, 0, True)

    response = test_client.get(f"/status/{job_id.hex}")
    response.raise_for_status()
    results = response.json()
    assert results["job_id"] == job_id.hex
    expected = {
        "padding": 0,
        "start_date": None,
        "stop_date": None,
        "target": "65P",
        "sources": ["neat_palomar_tricam"],
        "uncertainty_ellipse": False,
    }
    for k, v in expected.items():
        assert results["parameters"][k] == v

    expected = {
        "count": 0,
        "source": "neat_palomar_tricam",
        "source_name": "NEAT Palomar Tricam",
        "status": "finished",
    }
    for k, v in expected.items():
        assert results["status"][0][k] == v

    # date should be parsable by Time
    Time(results["status"][0]["date"])

    assert results["status"][0]["execution_time"] > 0

    # test invalid job id
    response = test_client.get(f"/status/invalid_job_id")
    assert response.status_code == 400
