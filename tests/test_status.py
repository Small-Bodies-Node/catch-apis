"""
A few simple tests to see that the API is working.

To see messages returned from the API, e.g., to debug failing tests:

    pytest --capture=tee-sys

These tests are currently hard-coded for DEPLOYMENT_TIER=LOCAL in .env.

"""

from catch_apis.app import app
import pytest

@pytest.fixture()
def test_client():
    return app.test_client()

def test_status_sources(test_client):
    response = test_client.get("/status/sources")
    response.raise_for_status()
    results = response.json()

    neat_palomar_tricam, = [row for row in results
                            if row['source'] == 'neat_palomar_tricam']
    assert neat_palomar_tricam['count'] == 128164
    assert neat_palomar_tricam['start_date'].startswith('2001-11-20')
    assert neat_palomar_tricam['stop_date'].startswith('2003-03-11')
