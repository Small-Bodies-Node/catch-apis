#!/usr/bin/env python

import argparse
import requests
from sseclient import SSEClient
from astropy.table import Table


def query_name(args):
    """Test target name with query/name route."""
    res = requests.get('{}/query/name'.format(args.base),
                       params={'name': args.target})
    data = res.json()
    print(data)
    if not data['valid']:
        raise ValueError('Invalid target name')


def query_moving(args):
    """Catch a moving object with query/moving route."""

    if args.name_test:
        # first, validate target name
        query_name(args)

    params = {
        'target': args.target,
        'cached': str(args.cached).lower()
    }
    res = requests.get('{}/query/moving'.format(args.base), params=params)
    data = res.json()
    print(data)

    if data['queued']:
        messages = SSEClient('{}/stream/{}'.format(args.base, data['job_id']))
        print('Connected to stream...')
        for msg in messages:
            if msg.data == data['job_id']:
                break
        print('...task completed.')

    res = requests.get(data['results'])
    data = res.json()
    if args.format == 'table':
        if data['count'] > 0:
            tab = Table(data['data'])
            tab.pprint(-1, -1)
        else:
            print('Nothing found.')
    else:
        print(data)


def listen_to_stream(args):
    """Inspect the CATCH event stream."""

    messages = SSEClient('{}/stream/{}'.format(args.base, args.job_id))
    print('Listening to event stream.  Use ctrl-c to stop.')

    try:
        for msg in messages:
            print(msg)
    except KeyboardInterrupt:
        pass


parser = argparse.ArgumentParser()
parser.add_argument('--base', default='https://musforti.astro.umd.edu/catch',
                    help='base URL for query, e.g., https://host/location')

subparsers = parser.add_subparsers(title='API routes')
parser_name = subparsers.add_parser('query/name')
parser_name.add_argument('target', help='moving target designation')
parser_name.set_defaults(func=query_name)

parser_moving = subparsers.add_parser('query/moving')
parser_moving.add_argument('target', help='moving target designation')
parser_moving.add_argument('--force', dest='cached', action='store_false',
                           help=('do not use cached results and force a '
                                 'new query'))
parser_moving.add_argument('--no-name-test', dest='name_test',
                           action='store_false',
                           help='skip target name testing')
parser_moving.add_argument('--format', choices=['json', 'table'],
                           default='table', help='output format')
parser_moving.set_defaults(func=query_moving)

parser_stream = subparsers.add_parser('stream')
parser_stream.add_argument('job_id', help='CATCH job ID')
parser_stream.set_defaults(func=listen_to_stream)

args = parser.parse_args()
if hasattr(args, 'func'):
    args.func(args)
else:
    parser.print_help()
