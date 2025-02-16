"""
A few simple tests to see that the API is working.

To see messages returned from the API, e.g., to debug failing tests:

    pytest --capture=tee-sys

These tests are currently hard-coded for DEPLOYMENT_TIER=LOCAL in .env.

"""

import sys
import json
import pytest
from unittest import mock
from functools import partial
from contextlib import contextmanager

import numpy as np
from typing import Tuple, List, Any, Optional
from starlette.testclient import TestClient
from catch_apis.config.env import ENV

# avoid interference from other REDIS queues
ENV.REDIS_JOBS = "REDIS_JOBS_TESTING"
ENV.REDIS_TASK_MESSAGES = "TASK_MESSAGES_TESTING"

from catch_apis.app import app
from catch_apis.services.stream import message_stream_service
from catch_apis import woRQer


@pytest.fixture()
def test_client() -> TestClient:
    return app.test_client()


@contextmanager
def mock_stream_messages(timeout):
    """Patch message stream to timeout in an absolute amount of time."""
    with mock.patch(
        "catch_apis.services.stream.messages_service",
        partial(message_stream_service, timeout),
    ):
        yield


# Only NEAT GEODSS will be searched
TARGET_EQUIVALENCIES = [
    ("65P", "65P/Gunn"),
    ("C/1995 O1", "C/1995 O1 (Hale-Bopp)"),
    ("2019 XS", "K19X00S"),
    ("1", "(1) Ceres"),
]

# limit to keys in the common data model (i.e., avoid survey-specific keys)
COMPARE_KEYS = [
    "airmass",
    "date",
    "ddec",
    "dec",
    "delta",
    "dra",
    "drh",
    "elong",
    "exposure",
    "filter",
    "mjd_start",
    "mjd_stop",
    "phase",
    "ra",
    "rh",
    "sangle",
    "seeing",
    "source",
    "source_name",
    "true_anomaly",
    "unc_a",
    "unc_b",
    "unc_theta",
    "vangle",
    "vmag",
]

# Number of matches updated 2022 Feb 6.  One target for each regex in
# src/services/query.py, except for the packed designations.
TARGET_MATCHES = [
    ("neat_maui_geodss", "65P", 9),
    ("neat_palomar_tricam", "73P", 15),
    ("neat_palomar_tricam", "73P-E", 9),
    ("neat_maui_geodss", "C/1995 O1", 23),
    ("neat_maui_geodss", "C/1996 J1-A", 9),
    ("neat_maui_geodss", "P/2002 JN16", 6),
    ("neat_maui_geodss", "2019 XS", 9),
    ("neat_maui_geodss", "1995 BT1", 6),
    ("skymapper_dr4", "A/2017 U1", 1),
    ("neat_maui_geodss", "1", 12),
    ("neat_palomar_tricam", "(2) Juno", 9),
    ("skymapper_dr4", "1I/`Oumuamua", 1),
]


def _query(
    test_client: TestClient,
    target: str,
    cached: bool,
    source: Optional[str] = None,
    **kwargs,
) -> Tuple[Any, bool]:

    parameters = {"target": target, "cached": cached}
    parameters.update(kwargs)

    if source is not None:
        parameters["sources"] = [source]

    catch_response = test_client.get("/catch", params=parameters)
    print(catch_response.url)
    catch_results = catch_response.json()

    queued = catch_results["queued"]
    if queued:
        # rather than use the message stream route, which will cause the test to
        # hang until the timeout is reached, run a worker in "burst" mode, then
        # directly read messages from the message function
        woRQer.run(True)
        messages = [message for message in message_stream_service(1)]
        for message in messages:
            if len(message) == 0 or not message.startswith("data:"):
                continue

            message_data = json.loads(message[6:])

            # print all messages for debugging
            print(str(message_data), file=sys.stderr)

            # only consider messages for our query
            if message_data["job_prefix"] != catch_results["job_id"][:8]:
                # this message is not for us
                continue

            # Message status may be 'success', 'error', 'running', 'queued'.
            if message_data["status"] == "error":
                raise ValueError(message_data["text"])

            if message_data["status"] == "success":
                break

    # "results" is the URL to the search results
    results_url = catch_results["results"].replace("http://testserver", "")
    caught_response = test_client.get(results_url)

    # response is JSON formatted
    caught_results = caught_response.json()

    return catch_results, caught_results, queued


@pytest.mark.parametrize("targets", TARGET_EQUIVALENCIES)
def test_equivalencies(test_client: TestClient, targets: List[str]) -> None:
    source = "neat_maui_geodss"
    catch0, caught0, queued0 = _query(test_client, targets[0], True, source=source)
    data0 = sorted(caught0["data"], key=lambda row: row["product_id"])
    assert len(data0) > 0
    for target in targets[1:]:
        catch, caught, queued = _query(test_client, target, True, source=source)
        data = sorted(caught["data"], key=lambda row: row["product_id"])
        for a, b in zip(data0, data):
            for k in COMPARE_KEYS:
                # np.isclose using rtol = 1% in case of ephemeris updates and
                # cached data
                assert (
                    a[k] == b[k]
                    if isinstance(a[k], (str, type(None)))
                    else np.isclose(a[k], b[k], rtol=0.01)
                )


@pytest.mark.parametrize("source,target,number", TARGET_MATCHES)
def test_cached_queries(
    test_client: TestClient,
    source: str,
    target: str,
    number: int,
) -> None:
    # run twice, once to search in case of no previous search,
    # the other to retrieve the cached data

    catch, caught, queued = _query(test_client, target, False, source=source)
    assert queued
    assert caught["count"] == number

    catch, caught, queued = _query(test_client, target, True, source=source)
    assert not queued
    assert caught["count"] == number


def test_padding_caching(test_client: TestClient):
    source = "neat_maui_geodss"
    target = "65P"
    number = 9

    catch, caught, queued = _query(test_client, target, False, source=source, padding=0)
    assert queued
    assert caught["count"] == number

    catch, caught, queued = _query(test_client, target, True, source=source, padding=0)
    assert not queued
    assert caught["count"] == number

    catch, caught, queued = _query(
        test_client, target, False, source=source, padding=0.001
    )
    assert queued
    assert caught["count"] == number

    catch, caught, queued = _query(
        test_client, target, True, source=source, padding=0.001
    )
    assert not queued
    assert caught["count"] == number


def test_ephemeris_uncertainties_are_null(test_client: TestClient):
    # regression test for #33

    # must be a target with undefined ephemeris uncertainties:
    catch, caught, queued = _query(test_client, "108P", True, "neat_palomar_tricam")

    for row in caught["data"]:
        assert row["unc_a"] is None
        assert row["unc_b"] is None
        assert row["unc_theta"] is None


def test_status_job_id(test_client: TestClient):
    catch, caught, queued = _query(
        test_client, TARGET_MATCHES[0][1], False, source=TARGET_MATCHES[0][0]
    )

    response = test_client.get(f"/status/{caught['job_id']}")
    data = response.json()
    assert data["job_id"] == caught["job_id"]
    assert data["parameters"]["target"] == "65P"
    assert not data["parameters"]["uncertainty_ellipse"]
    assert data["parameters"]["padding"] == 0
    assert data["status"][0]["source"] == "neat_maui_geodss"
    assert data["status"][0]["source_name"] == "NEAT Maui GEODSS"
    assert len(data["status"][0]["date"]) > 10
    assert data["status"][0]["status"] == "finished"
    assert data["status"][0]["execution_time"] > 0
    assert data["status"][0]["count"] == TARGET_MATCHES[0][2]

    catch, caught, queued = _query(
        test_client, TARGET_MATCHES[0][1], True, source=TARGET_MATCHES[0][0]
    )
    response = test_client.get(f"/status/{caught['job_id']}")
    data = response.json()
    assert data["job_id"] == caught["job_id"]
    assert data["status"][0]["execution_time"] is None
