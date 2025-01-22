# Licensed with the 3-clause BSD license.  See LICENSE for details.

import numpy as np
from starlette.testclient import TestClient
from . import fixture_test_client


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
    assert "neat_palomar_tricam" in results["query"]["sources"]
    assert len(results["data"]) == 4
    assert {
        obs["product_id"][obs["product_id"].rindex("_") + 1 :]
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
    assert "neat_palomar_tricam" in results["query"]["sources"]
    assert len(results["data"]) == 4
    assert all(
        [
            row["fov"]
            == "7.500000:-12.500000,12.500000:-12.500000,12.500000:-7.500000,7.500000:-7.500000"
            for row in results["data"]
        ]
    )
    assert {
        obs["product_id"][obs["product_id"].rindex("_") + 1 :]
        for obs in results["data"]
    } == set([str(5 + 49 * i) for i in range(4)])


def test_point_date_range(test_client: TestClient):
    parameters = {
        "ra": "00:34:32.0",
        "dec": "+8 00 48",
        "sources": ["neat_palomar_tricam"],
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
        "sources": ["neat_palomar_tricam"],
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

    parameters = {
        "ra": "00:00",
        "dec": "+0 0",
        "sources": ["neat_palomar_tricam"],
        "radius": np.hypot(5, 5) / 2 * 60 + 1,
        "intersection_type": "AreaContainsImage",
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 4
