"""
A few simple tests to see that the API is working.

To see messages returned from the API, e.g., to debug failing tests:

    pytest --capture=tee-sys

These tests are currently hard-coded for DEPLOYMENT_TIER=LOCAL in .env.

"""
from typing import Tuple, List, Any
import sys
import json
import requests
import pytest
from sseclient import SSEClient


TARGET_EQUIVALENCIES = [
    ('65P', '65P/Gunn'),
    ('C/1995 O1', 'C/1995 O1 (Hale-Bopp)'),
    ('2019 XS', 'K19X00S'),
    ('1', '(1) Ceres'),
]
COMPARE_KEYS = ['airmass', 'ddec', 'dec', 'delta', 'dra', 'exposure', 'filter',
                'jd', 'phase', 'ra', 'rdot', 'rh', 'sangle', 'selong', 'source',
                'tmtp', 'trueanomaly', 'unc_a', 'unc_b', 'unc_theta', 'vangle',
                'vmag']


# number of matches updated 2022 Jan 31
TARGET_MATCHES = [
    ('65P', 15),
    ('C/1995 O1', 30),
    ('2019 XS', 14),
    ('1', 26),
    ('2I/Borisov', 0)
]


def _query(target: str, cached: bool) -> Tuple[Any, bool]:
    res = requests.get('http://127.0.0.1:5003/api/query/moving',
                       params={'target': target,
                               'cached': cached})
    data = res.json()

    queued = data['queued']
    if queued:
        messages = SSEClient('http://127.0.0.1:5003/api/stream')
        for message in messages:
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

    # 'results' is the URL to the search results
    res = requests.get(data['results'])

    # response is JSON formatted
    data = res.json()

    return data, queued


@pytest.mark.parametrize('targets', TARGET_EQUIVALENCIES)
def test_equivalencies(targets: List[str]) -> None:
    q0 = _query(targets[0], True)[0]['data']
    assert len(q0) > 0
    for target in targets[1:]:
        q = _query(target, True)[0]['data']
        for a, b in zip(q0, q):
            for k in COMPARE_KEYS:
                assert a[k] == b[k]


@pytest.mark.parametrize('target,number', TARGET_MATCHES)
def test_cached_queries(target: str, number: int) -> None:
    # run twice, once to search in case of no previous search,
    # the other to retrieve the cached data

    q, queued = _query(target, False)
    assert queued
    assert q['count'] == number

    q, queued = _query(target, True)
    assert not queued
    assert q['count'] == number
