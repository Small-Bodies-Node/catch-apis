# Licensed with the 3-clause BSD license.  See LICENSE for details.

import numpy as np
from starlette.testclient import TestClient
from . import fixture_test_client  # noqa F401
import catch_apis.api.fixed
from catch_apis.api.fixed import fixed_target_query_controller, CatchApisException


def test_invalid_queries():
    result = fixed_target_query_controller("bad ra", "1")
    assert result["error"]
    assert "Invalid ra" in result["message"]

    result = fixed_target_query_controller("1d", "10d", start_date="invalid date")
    assert result["error"]
    assert "Invalid start_date" in result["message"]


def test_service_exceptions(test_client: TestClient, monkeypatch):
    def error(*args, **kwargs):
        raise CatchApisException("APIs exception")

    monkeypatch.setattr(catch_apis.api.fixed, "fixed_target_query_service", error)

    parameters = {
        "ra": "00:34:32.0",  # 8.63 deg
        "dec": "+8 00 48",  # 8.01 deg
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["error"]
    assert "APIs exception" in results["message"]

    def error(*args, **kwargs):
        raise RuntimeError

    monkeypatch.setattr(catch_apis.api.fixed, "fixed_target_query_service", error)
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["error"]
    assert "Unexpected error" in results["message"]


def test_point_full_search(test_client: TestClient):
    parameters = {
        "ra": "00:34:32.0",  # 8.63 deg
        "dec": "+8 00 48",  # 8.01 deg
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()

    assert results["message"] == ""
    assert np.isclose(results["query"]["ra"], ((34 + 32 / 60) / 60) * 15)
    assert np.isclose(results["query"]["dec"], 8 + 48 / 60 / 60)
    assert "test_sky_survey" in results["query"]["sources"]
    assert len(results["data"]) == 4
    assert {
        obs["product_id"][obs["product_id"].rindex("_") + 1 :]  # noqa E203
        for obs in results["data"]
    } == set([str(7 * 4 + 5 + 49 * i) for i in range(4)])

    # try negative dec
    parameters = {
        "ra": "00:34:32.0",  # 8.63 deg
        "dec": "-8 00 48",  # -8.01 deg
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()

    assert results["message"] == ""
    assert np.isclose(results["query"]["ra"], ((34 + 32 / 60) / 60) * 15)
    assert np.isclose(results["query"]["dec"], -8 - 48 / 60 / 60)
    assert "test_sky_survey" in results["query"]["sources"]
    assert len(results["data"]) == 4
    assert all(
        [
            row["fov"]
            == "7.500000:-12.500000,12.500000:-12.500000,12.500000:-7.500000,7.500000:-7.500000"
            for row in results["data"]
        ]
    )
    assert {
        obs["product_id"][obs["product_id"].rindex("_") + 1 :]  # noqa E203
        for obs in results["data"]
    } == set([str(5 + 49 * i) for i in range(4)])


def test_point_date_range(test_client: TestClient):
    parameters = {
        "ra": "00:34:32.0",
        "dec": "+8 00 48",
        "sources": ["test_sky_survey"],
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["start_date"] is None
    assert results["query"]["stop_date"] is None
    assert len(results["data"]) == 4

    parameters["start_date"] = "2012-03-14 01:00"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["start_date"] == "2012-03-14 01:00:00.000"
    assert len(results["data"]) == 2

    parameters["stop_date"] = "2012-03-14 01:30"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["stop_date"] == "2012-03-14 01:30:00.000"
    assert len(results["data"]) == 1

    del parameters["start_date"]
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["start_date"] is None
    assert len(results["data"]) == 3


def test_areal_search(test_client: TestClient):
    parameters = {
        "ra": "00:34:32.0",
        "dec": "+8 00 48",
        "sources": ["test_sky_survey"],
        "radius": 35,
        "intersection_type": "ImageIntersectsArea",
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 8

    parameters["intersection_type"] = "ImageContainsArea"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 0

    parameters["intersection_type"] = "AreaContainsImage"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 0
