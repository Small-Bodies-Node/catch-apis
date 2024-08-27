# Licensed with the 3-clause BSD license.  See LICENSE for details.

from starlette.testclient import TestClient
from . import fixture_test_client


def test_status_sources2(test_client: TestClient):
    response = test_client.get("/status/sources")
    response.raise_for_status()
    results = response.json()

    (neat_palomar_tricam,) = [
        row for row in results if row["source"] == "neat_palomar_tricam"
    ]
    assert neat_palomar_tricam["count"] == 49 * 4
    assert neat_palomar_tricam["start_date"].startswith("2012-03-14")
    assert neat_palomar_tricam["stop_date"].startswith("2012-03-14")
