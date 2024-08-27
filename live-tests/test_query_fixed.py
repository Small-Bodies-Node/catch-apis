"""
A few simple tests to see that the API is working.

To see messages returned from the API, e.g., to debug failing tests:

    pytest --capture=tee-sys

These tests are currently hard-coded for DEPLOYMENT_TIER=LOCAL in .env.

"""

import pytest
from starlette.testclient import TestClient
import numpy as np
from catch_apis.app import app

@pytest.fixture()
def test_client() -> TestClient:
    return app.test_client()

def test_point_full_search(test_client: TestClient):
    # Crab nebula
    parameters = {
        "ra": "05:34:32.0",
        "dec": "+22 00 48",
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()

    assert results["message"] == ""
    assert np.isclose(results["query"]["ra"], (5 + (34 + 32 / 60) / 60) * 15)
    assert np.isclose(results["query"]["dec"], 22 + 48 / 60 / 60)
    assert "neat_palomar_tricam" in results["query"]["sources"]
    assert len(results["data"]) == 428
    product_ids = [obs["product_id"] for obs in results["data"]]

    # these are verified to be the Crab:
    assert "rings.v3.skycell.1784.059.wrp.g.55560_46188.fits" in product_ids
    assert "urn:nasa:pds:gbo.ast.catalina.survey:data_calibrated:703_20211108_2b_n24018_01_0002.arch" in product_ids

def test_point_date_range(test_client: TestClient):
    # Crab nebula
    parameters = {
        "ra": "05:34:32.0",
        "dec": "+22 00 48",
        "sources": ["spacewatch"],
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["start_date"] is None
    assert results["query"]["stop_date"] is None
    assert len(results["data"]) == 167

    parameters["start_date"] = "2007-01-01"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["start_date"] == "2007-01-01 00:00:00.000"
    assert len(results["data"]) == 118

    parameters["stop_date"] = "2008-01-01"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["stop_date"] == "2008-01-01 00:00:00.000"
    assert len(results["data"]) == 24
    
    del parameters["start_date"]
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert results["query"]["start_date"] is None
    assert len(results["data"]) == 73

    # 118 + 73 - 24 = 167

def test_areal_search(test_client: TestClient):
    # Crab nebula
    parameters = {
        "ra": "05:34:32.0",
        "dec": "+22 00 48",
        "sources": ["ps1dr2"],
        "radius": 1,
        "intersection_type": "ImageIntersectsArea",
    }
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 223

    parameters["intersection_type"] = "ImageContainsArea"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 73

    parameters["intersection_type"] = "AreaContainsImage"
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 0

    # should match ImageContainsArea
    parameters["radius"] = 32
    response = test_client.get("/fixed", params=parameters)
    response.raise_for_status()
    results = response.json()
    assert len(results["data"]) == 73