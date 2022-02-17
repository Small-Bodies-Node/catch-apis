"""
A few simple tests to see that the API is working.

To see messages returned from the API, e.g., to debug failing tests:

    pytest --capture=tee-sys

These tests are currently hard-coded for DEPLOYMENT_TIER=LOCAL in .env.

"""
from typing import Tuple, List, Any, Optional
import sys
import json
import requests
import pytest
from sseclient import SSEClient


# Only NEAT GEODSS will be searched
TARGET_EQUIVALENCIES = [
    ('65P', '65P/Gunn'),
    ('C/1995 O1', 'C/1995 O1 (Hale-Bopp)'),
    ('2019 XS', 'K19X00S'),
    ('1', '(1) Ceres'),
]

# limit to keys in the common data model (i.e., avoid survey-specific keys)
COMPARE_KEYS = ['airmass', 'date', 'ddec', 'dec', 'delta', 'dra', 'drh',
                'elong', 'exposure', 'filter', 'mjd_start', 'mjd_stop',
                'phase', 'ra', 'rh', 'sangle', 'seeing', 'source',
                'source_name', 'true_anomaly', 'unc_a', 'unc_b', 'unc_theta',
                'vangle', 'vmag']

# Number of matches updated 2022 Feb 6.  One target for each regex in
# src/services/query.py, except for the packed designations.
TARGET_MATCHES = [
    ('neat_maui_geodss', '65P', 9),
    ('neat_palomar_tricam', '73P', 15),
    ('neat_palomar_tricam', '73P-E', 9),
    ('neat_maui_geodss', 'C/1995 O1', 23),
    ('neat_maui_geodss', 'C/1996 J1-A', 9),
    ('neat_maui_geodss', 'P/2002 JN16', 6),
    ('neat_maui_geodss', '2019 XS', 9),
    ('neat_maui_geodss', '1995 BT1', 6),
    ('skymapper', 'A/2017 U1', 2),
    ('neat_maui_geodss', '1', 12),
    ('neat_palomar_tricam', '(2) Juno', 9),
    ('skymapper', '1I/`Oumuamua', 2)
]


def _query(target: str, cached: bool, source: Optional[str] = None
           ) -> Tuple[Any, bool]:

    parameters = {
        'target': target,
        'cached': cached
    }
    if source is not None:
        parameters['sources'] = [source]

    res = requests.get('http://127.0.0.1:5000/catch',
                       params=parameters)
    print(res.url)
    data = res.json()

    queued = data['queued']
    if queued:
        messages = SSEClient('http://127.0.0.1:5000/stream')
        for message in messages:
            if len(message.data) == 0:
                continue

            message_data = json.loads(message.data)

            # print all messages for debugging
            print(str(message_data), file=sys.stderr)

            # edit out keep-alive messages
            if not isinstance(message_data, dict):
                continue

            # only consider messages for our query
            if message_data['job_prefix'] != data['job_id'][:8]:
                # this mesage is not for us
                continue

            # Message status may be 'success', 'error', 'running', 'queued'.
            if message_data['status'] == 'error':
                raise ValueError(message_data['text'])

            if message_data['status'] == 'success':
                break

        del messages

    # 'results' is the URL to the search results
    res = requests.get(data['results'])

    # response is JSON formatted
    data = res.json()

    return data, queued


@pytest.mark.parametrize('targets', TARGET_EQUIVALENCIES)
def test_equivalencies(targets: List[str]) -> None:
    source = 'neat_maui_geodss'
    q0 = _query(targets[0], True, source=source)[0]['data']
    assert len(q0) > 0
    for target in targets[1:]:
        q = _query(target, True, source=source)[0]['data']
        for a, b in zip(q0, q):
            for k in COMPARE_KEYS:
                assert a[k] == b[k]


@pytest.mark.parametrize('source,target,number', TARGET_MATCHES)
def test_cached_queries(source: str, target: str, number: int) -> None:
    # run twice, once to search in case of no previous search,
    # the other to retrieve the cached data

    q, queued = _query(target, False, source=source)
    assert queued
    assert q['count'] == number

    q, queued = _query(target, True, source=source)
    assert not queued
    assert q['count'] == number
