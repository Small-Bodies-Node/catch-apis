# Licensed with the 3-clause BSD license.  See LICENSE for details.

import pytest
import numpy as np
from starlette.testclient import TestClient
import catch_apis.api.catch
from catch_apis.api.catch import catch_controller
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
