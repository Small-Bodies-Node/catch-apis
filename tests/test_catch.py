# Licensed with the 3-clause BSD license.  See LICENSE for details.

import uuid
import pytest
import numpy as np
from starlette.testclient import TestClient
import catch_apis.api.catch
from catch_apis.api.catch import catch_controller
from catch_apis.tasks.catch import catch_task
from catch_apis.config.env import ENV
from catch_apis.config import QueryStatus, allowed_sources
from . import fixture_test_client, mock_flask_request, mock_redis, MockedJobsQueue


class TestCatchController:
    def test_target_error(self):
        # empty target string
        result = catch_controller("")
        assert result["error"]
        assert not result["queued"]
        assert "Invalid target" in result["message"]

        # bare name, which has an ambiguous target_type
        result = catch_controller("encke")
        assert result["error"]
        assert not result["queued"]
        assert "ambiguous" in result["message"]

    def test_date_error(self):
        result = catch_controller("2P", start_date="yesterday")
        assert result["error"]
        assert not result["queued"]
        assert "Invalid start_date" in result["message"]

        result = catch_controller("2P", stop_date="yesteryear")
        assert result["error"]
        assert not result["queued"]
        assert "Invalid stop_date" in result["message"]

    def test_queued(self, test_client: TestClient, mock_redis):
        response = test_client.get(f"/catch", params={"target": "2P", "cached": True})
        response.raise_for_status()
        results = response.json()

        assert uuid.UUID(results["job_id"]).version == 4
        assert not results["error"]
        assert results["queued"]
        assert not results["queue_full"]
        assert results["results"] == f"http://testserver/caught/{results['job_id']}"
        assert results["message_stream"] == "http://testserver/stream"
        assert results["query"]["target"] == "2P"
        assert set(results["query"]["sources"]) == set(allowed_sources)
        assert results["query"]["start_date"] is None
        assert results["query"]["stop_date"] is None
        assert not results["query"]["uncertainty_ellipse"]
        assert np.isclose(results["query"]["padding"], 0)
        assert results["query"]["cached"]

    @pytest.mark.remote
    def test_cached(self, test_client: TestClient, mock_redis):
        # first, cache a query
        job_id = uuid.uuid4()
        catch_task(job_id, "3910", ["neat_palomar_tricam"], None, None, False, 0, False)

        # re-run, fetching the cached result
        response = test_client.get(
            f"/catch",
            params={
                "target": "3910",
                "sources": ["neat_palomar_tricam"],
                "cached": True,
            },
        )
        response.raise_for_status()
        results = response.json()

        assert results["job_id"] != job_id.hex
        assert not results["error"]
        assert not results["queued"]
        assert not results["queue_full"]
        assert results["results"] == f"http://testserver/caught/{results['job_id']}"

    def test_queue_accounting(
        self,
        test_client: TestClient,
        mock_redis,
        mock_flask_request,
        monkeypatch,
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
