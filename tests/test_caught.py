# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
import pytest
import numpy as np
from starlette.testclient import TestClient
from catch_apis.api.caught import caught_controller
from catch_apis.tasks.catch import catch_task
from . import fixture_test_client, mock_redis


def test_caught(test_client: TestClient, mock_redis):
    job_id = uuid.uuid4()
    catch_task(job_id, "3910", ["test_sky_survey"], None, None, False, 0, True)

    response = test_client.get(f"/caught/{job_id.hex}")
    response.raise_for_status()
    results = response.json()

    assert results["count"] == 4
    assert len(results["status"]) == 1
    assert results["status"][0]["count"] == 4

    # one of the expected results
    expected = {
        "airmass": None,
        "archive_url": "http://testserver/test/data/164.fits",
        "cutout_url": "http://testserver/test/data/164.fits?ra=0.33597&dec=0.11356&size=0.1",
        "date": "2012-03-14 01:40:46.000",
        "ddec": 28.58443,
        "dec": 0.11356,
        "delta": 3.72217277975446,
        "diff_url": None,
        "dra": 56.70584,
        "drh": 2.3627547,
        "elong": 6.6455,
        "exposure": None,
        "filter": None,
        "found_id": 1,
        "fov": "-2.500000:-2.500000,2.500000:-2.500000,2.500000:2.500000,-2.500000:2.500000",
        "maglimit": None,
        "mjd_start": 56000.069803240454,
        "mjd_stop": 56000.07015046268,
        "observation_id": 164,
        "phase": 2.4115,
        "preview_url": "http://testserver/test/data/164.fits?ra=0.33597&dec=0.11356&size=jpeg",
        "product_id": "urn:nasa:pds:gbo.ast.tss:data:164",
        "ra": 0.33597,
        "rh": 2.737041603991,
        "sangle": 246.811,
        "seeing": None,
        "source": "test_sky_survey",
        "source_name": "Test Sky Survey",
        "true_anomaly": 88.5703,
        "unc_a": 0.00162,
        "unc_b": 0.00035,
        "unc_theta": 34.168,
        "vangle": 57.91,
        "vmag": 17.327,
    }
    i = [result["product_id"] for result in results["data"]].index(
        expected["product_id"]
    )
    for k, v in results["data"][i].items():
        if isinstance(v, float):
            assert np.isclose(expected[k], v, rtol=1e-3)
        elif v is None:
            assert expected[k] is None
        else:
            assert expected[k] == v


def test_invalid_job_id(test_client: TestClient):
    response = test_client.get(f"/caught/invalid_job_id")
    assert response.status_code == 400
    assert response.content == b'"Invalid job ID"\n'
