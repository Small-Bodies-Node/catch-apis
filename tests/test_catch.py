# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
import pytest
import numpy as np
from starlette.testclient import TestClient
import catch_apis.api.catch
from catch_apis.api.catch import catch_controller
from catch_apis.tasks.catch import catch_task
from catch_apis.config.env import ENV
from catch_apis.config import QueryStatus
from . import fixture_test_client, mock_flask_request, mock_redis, MockedJobsQueue


def test_catch_controller_queue_accounting(
    test_client: TestClient, mock_redis, mock_flask_request, monkeypatch
):
    queue = MockedJobsQueue()

    def mock_catch_service(*args, **kwargs):
        try:
            mock_catch_service.count += 1
        except AttributeError:
            mock_catch_service.count = 1

        queue.enqueue(f=None, args=args)

        return (
            QueryStatus.QUEUED
            if mock_catch_service.count <= ENV.REDIS_JOBS_MAX_QUEUE_SIZE
            else QueryStatus.QUEUEFULL
        )

    monkeypatch.setattr(catch_apis.api.catch, "catch_service", mock_catch_service)
    monkeypatch.setattr(catch_apis.api.catch, "JobsQueue", lambda: queue)

    for i in range(ENV.REDIS_JOBS_MAX_QUEUE_SIZE + 2):
        result = catch_controller("65P", cached=False)
        if i < ENV.REDIS_JOBS_MAX_QUEUE_SIZE:
            assert result["queued"]
            assert not result["queue_full"]
            assert result["queue_position"] == i
        else:
            assert not result["queued"]
            assert result["queue_full"]
            assert result["queue_position"] is None


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
