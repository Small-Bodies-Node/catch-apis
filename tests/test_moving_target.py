# Licensed with the 3-clause BSD license.  See LICENSE for details.
"""
The following objects, brighter than V = 16, were found in the 300.0-arcminute region around R.A. = 00 00 00.0, Decl. = +00 00 00 (J2000.0) on 2012 03 14.05 UT:

 Object designation         R.A.      Decl.     V       Offsets     Motion/hr   Orbit  Further observations?
                           h  m  s     °  '  "        R.A.   Decl.  R.A.  Decl.        Comment (Elong/Decl/V at date 1)

   (208) Lacrimosa       23 56 01.9 -00 31 36  14.8  59.5W  31.6S    54+    24+   71o  None needed at this time.
    P/2011 S1 (Gibbs)    23 59 03.8 +01 28 26        14.1W  88.4N    22+     9+  cmt   (r =   7.35 AU)
   (182) Elsa            23 59 02.4 -01 32 19  13.5  14.4W  92.3S    75+    32+   62o  None needed at this time.
    C/2021 U5 (Catalina) 23 59 52.7 +01 36 12         1.8W  96.2N     6+     2+  cmt   (r =  23.42 AU)
    P/2019 V2 (Groeller) 00 01 01.6 +01 40 21        15.4E 100.3N    15+     6+  cmt   (r =   9.87 AU)
   (829) Academia        23 52 48.3 +00 05 07  16.0 107.9W   5.1N    65+    33+   44o  None needed at this time.
   (279) Thule           00 02 16.4 -01 43 46  15.6  34.1E 103.8S    37+    16+   70o  None needed at this time.
   (499) Venusia         00 01 21.4 +01 51 32  15.9  20.4E 111.5N    45+    19+   57o  None needed at this time.
   (670) Ottegebe        00 09 37.7 -00 04 03  14.2 144.4E   4.0S    73+    27+   57o  None needed at this time.
 116P/Wild               23 52 57.5 -02 00 48       105.6W 120.8S    32+    14+  cmt   (r =   4.67 AU)
  (1147) Stavropolis     23 52 22.5 +02 01 10  16.0 114.4W 121.2N    75+    32+   41o  None needed at this time.
         1935 UZ         23 56 11.7 -02 48 53        57.1W 168.9S    89+    36+    4d  Leave for survey recovery.
   (113) Amalthea        00 04 15.8 -02 55 45  13.6  64.0E 175.7S    61+    25+   86o  None needed at this time.
   (538) Friederike      00 01 04.1 -03 11 04  14.8  16.0E 191.1S    62+    24+   60o  None needed at this time.
   (217) Eudora          00 10 57.7 -01 50 24  14.5 164.4E 110.4S    76+    27+   52o  None needed at this time.
    P/2023 T1 (PANSTARRS 23 56 20.5 +03 18 43        54.9W 198.7N    25+    10+  cmt   (r =   6.18 AU)
    C/2012 E2 (SWAN)     23 59 06.6 -03 27 51        13.4W 207.9S   492-   189+  cmt   (r =   0.10 AU)
   (190) Ismene          00 14 23.6 +00 36 48  14.5 215.9E  36.8N    43+    16+   75o  None needed at this time.
     (9) Metis           00 09 39.2 -02 46 54  11.0 144.8E 166.9S    69+    31+   86o  None needed at this time.
 270P/Gehrels            00 10 10.0 +02 44 41       152.5E 164.7N    36+    15+  cmt   (r =   4.59 AU)
 483P-A/PANSTARRS        23 50 04.8 +03 04 43       148.8W 184.7N    49+    16+  cmt   (r =   3.30 AU)
 483P-B/PANSTARRS        23 50 02.9 +03 04 39       149.3W 184.6N    49+    16+  cmt   (r =   3.30 AU)
         2010 FL106      00 16 15.1 -00 41 04       243.8E  41.1S    76+    39+    1d  Leave for survey recovery.
  25D/Neujmin 2          23 45 37.0 +02 10 03       215.7W 130.1N    31+    13+  cmt   (r =   4.64 AU)
    P/2004 R3 (LINEAR-NE 23 56 02.8 +04 14 38        59.3W 254.6N    70+    34+  cmt   (r =   2.32 AU)
    A/2020 M4            23 51 40.0 -03 57 50       125.0W 237.8S     5+     2+  cmt   (r =  19.52 AU)
    P/2020 B4 (Sheppard) 00 17 30.5 +01 54 48       262.6E 114.8N    16+     6+  cmt   (r =   9.45 AU)
 418P/LINEAR             23 53 16.2 +04 34 40       101.0W 274.7N    27+    11+  cmt   (r =   5.53 AU)
   (193) Ambrosia        23 40 51.4 -01 08 51  14.2 287.1W  68.8S    68+    36+   47o  None needed at this time.
"""

import sys
import json
import pytest
from unittest import mock
from functools import partial
from typing import Any, List, Tuple
from contextlib import contextmanager

import numpy as np
from starlette.testclient import TestClient

from catch_apis.services.stream import messages as stream_messages
from catch_apis import woRQer
from . import fixture_test_client


@contextmanager
def mock_stream_messages(timeout):
    """Patch message stream to timeout in an absolute amount of time."""
    with mock.patch(
        "catch_apis.services.stream.messages",
        partial(stream_messages, timeout),
    ):
        yield


TARGET_EQUIVALENCIES = [
    ("116P", "116P/Wild 4"),
    ("C/2012 E2", "C/2012 E2 (SWAN)"),
    ("2010 FL106", "K10FA6L"),
    ("208", "(208) Lacrimosa"),
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

# One target for each regex in src/services/query.py, except for the packed
# designations.
TARGET_MATCHES = [
    ("neat_palomar_tricam", "116P", 4),
    ("neat_palomar_tricam", "483P-A", 4),
    ("neat_palomar_tricam", "C/2021 U5", 4),
    ("neat_palomar_tricam", "C/1996 J1-A", 0),
    ("neat_palomar_tricam", "P/2019 V2", 4),
    ("neat_palomar_tricam", "2010 FL106", 4),
    ("neat_palomar_tricam", "A/2020 M4", 4),
    ("neat_palomar_tricam", "113", 4),
    ("neat_palomar_tricam", "(9) Metis", 4),
    ("neat_palomar_tricam", "1I/`Oumuamua", 0),
]


def _query(
    test_client: TestClient,
    target: str,
    cached: bool,
    source: str | None = None,
    **kwargs,
) -> Tuple[Any, bool]:

    parameters = {"target": target, "cached": cached}
    parameters.update(kwargs)

    if source is not None:
        parameters["sources"] = [source]

    catch_response = test_client.get("/catch", params=parameters)
    catch_results = catch_response.json()

    queued = catch_results["queued"]
    if queued:
        # rather than use the message stream route, which will cause the test to
        # hang until the timeout is reached, run a worker in "burst" mode, then
        # directly read messages from the message function
        woRQer.run(True)
        messages = [message for message in stream_messages(1)]
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
    source = "neat_palomar_tricam"
    catch0, caught0, queued0 = _query(test_client, targets[0], True, source=source)
    data0 = caught0["data"]
    assert len(data0) > 0
    for target in targets[1:]:
        catch, caught, queued = _query(test_client, target, True, source=source)
        data = caught["data"]
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
    source = "neat_palomar_tricam"
    target = "116P"
    number = 4

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
    assert data["parameters"]["target"] == "116P"
    assert not data["parameters"]["uncertainty_ellipse"]
    assert data["parameters"]["padding"] == 0
    assert data["status"][0]["source"] == "neat_palomar_tricam"
    assert data["status"][0]["source_name"] == "NEAT Palomar Tricam"
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
