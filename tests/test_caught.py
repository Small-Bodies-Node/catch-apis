# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
import pytest
import numpy as np
from starlette.testclient import TestClient
from catch_apis.tasks.catch import catch_task
from . import fixture_test_client, mock_redis


def test_caught(test_client: TestClient, mock_redis):
    job_id = uuid.uuid4()
    catch_task(job_id, "3910", ["neat_palomar_tricam"], None, None, False, 0, True)

    response = test_client.get(f"/caught/{job_id.hex}")
    response.raise_for_status()
    results = response.json()

    assert results["count"] == 4
    assert len(results["status"]) == 1
    assert results["status"][0]["count"] == 4
    expected = {
        "airmass": None,
        "archive_url": "https://sbnarchive.psi.edu/pds4/surveys/gbo.ast.neat.survey/data_tricam/p20011126/obsdata/66.fit.fz",
        "cutout_url": "https://sbnsurveys.astro.umd.edu/api/images/urn:nasa:pds:gbo.ast.neat.survey:data_tricam:p20011126_obsdata_66?ra=0.32013&dec=0.10556&size=7.20arcmin&format=fits",
        "date": "2012-03-14 00:40:20.000",
        "ddec": 28.58548,
        "dec": 0.10556,
        "delta": 3.72202908386062,
        "diff_url": None,
        "dra": 56.57677,
        "drh": 2.3627453,
        "elong": 6.6695,
        "exposure": None,
        "filter": None,
        "fov": "-2.500000:-2.500000,2.500000:-2.500000,2.500000:2.500000,-2.500000:2.500000",
        "maglimit": None,
        "mjd_start": 56000.027835648034,
        "mjd_stop": 56000.02818287026,
        "phase": 2.4201,
        "preview_url": "https://sbnsurveys.astro.umd.edu/api/images/urn:nasa:pds:gbo.ast.neat.survey:data_tricam:p20011126_obsdata_66?ra=0.32013&dec=0.10556&size=7.20arcmin&format=jpeg",
        "product_id": "urn:nasa:pds:gbo.ast.neat.survey:data_tricam:p20011126_obsdata_66",
        "ra": 0.32013,
        "rh": 2.736984336056,
        "sangle": 246.81799999999998,
        "seeing": None,
        "source": "neat_palomar_tricam",
        "source_name": "NEAT Palomar Tricam",
        "true_anomaly": 88.5612,
        "unc_a": 0.00162,
        "unc_b": 0.00035,
        "unc_theta": 34.167,
        "vangle": 57.91,
        "vmag": 17.328,
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
