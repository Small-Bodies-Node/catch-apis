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
    assert {obs["product_id"] for obs in results["data"]} == set(
        [str(7 * 4 + 5 + 49 * i) for i in range(4)]
    )
