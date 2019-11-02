#!/usr/bin/env python

import argparse
import urllib.parse

import requests
from sseclient import SSEClient
from astropy.table import Table

parser = argparse.ArgumentParser()
parser.add_argument('target', default='65P')
parser.add_argument('--base', default='https://musforti.astro.umd.edu/catch',
                    help='base URL for query, e.g., https://host/location')
parser.add_argument('--force', dest='cached', action='store_false',
                    help='do not use cached results and force a new query')
parser.add_argument('--test-target', action='store_true',
                    help='only test the target name')
args = parser.parse_args()

res = requests.get('{}/query/target'.format(args.base),
                   params={'name': args.target})
data = res.json()
print(data)
if not data['valid']:
    raise ValueError('Invalid target name')

# exit without error
if args.test_target:
    exit(0)

params = {
    'target': args.target,
    'cached': str(args.cached).lower()
}
res = requests.get('{}/query/moving'.format(args.base), params=params)
data = res.json()
print(data)

if data['queued']:
    messages = SSEClient('{}/stream'.format(args.base))
    for msg in messages:
        if msg.data == data['job_id']:
            break
    print('task completed')

res = requests.get(data['results'])
data = res.json()
if data['count'] > 0:
    tab = Table(data['data'])
    tab.pprint(-1, -1)
else:
    print('Nothing found')
