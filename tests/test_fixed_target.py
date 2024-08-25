# Licensed with the 3-clause BSD license.  See LICENSE for details.

import pytest
import numpy as np
from starlette.testclient import TestClient
from . import test_client
from catch_apis.config.env import ENV


def test_point_full_search(test_client: TestClient):
    assert ENV.REDIS_JOBS == "TEST_JOBS"
    print(ENV.DB_DATABASE)

    # Crab nebula
    parameters = {
        "ra": "00:34:32.0",
        "dec": "+8 00 48",
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
