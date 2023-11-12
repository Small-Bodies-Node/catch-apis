"""
A few simple tests to see that the API is working.

To see messages returned from the API, e.g., to debug failing tests:

    pytest --capture=tee-sys

These tests are currently hard-coded for DEPLOYMENT_TIER=LOCAL in .env.

"""

import requests

def test_status_sources():
    res = requests.get('http://127.0.0.1:5000/status/sources')
    data = res.json()
    neat_palomar_tricam, = [row for row in data
                            if row['source'] == 'neat_palomar_tricam']
    assert neat_palomar_tricam['count'] == 131389
    assert neat_palomar_tricam['start_date'].startswith('2001-11-20')
    assert neat_palomar_tricam['stop_date'].startswith('2003-03-11')
