#!/usr/bin/env python3
import time
import sys
import argparse
import json
from typing import Tuple, Any
import requests
from sseclient import SSEClient


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:5000')
    parser.add_argument('--target', default='65P')
    parser.add_argument('--source', '-s', default=None, action='append')
    parser.add_argument('--no-cached', '--force', '-f',
                        action='store_false', dest='cached')
    parser.add_argument('-v', dest='verbose', action='store_true',
                        help='verbose mode')
    return parser.parse_args()


def query(args: argparse.Namespace) -> Tuple[str, float, Any]:
    start = time.monotonic()

    params = {
        'target': args.target,
        'cached': args.cached
    }
    if args.source is not None:
        params['sources'] = args.source

    res = requests.get(f'{args.url}/catch', params=params)
    data = res.json()
    if args.verbose:
        print(data)
        print()

    if data['queued']:
        messages = SSEClient(data['message_stream'], chunk_size=128)
        for message in messages:
            if len(message.data) == 0:
                continue

            if args.verbose:
                print(message.data)

            message_data = json.loads(message.data)

            # edit out keep-alive messages
            if not isinstance(message_data, dict):
                continue

            if message_data['job_prefix'] != data['job_id'][:8]:
                # this mesage is not for us
                continue

            # this message is for us, print the text
            print(message_data['text'], file=sys.stderr)

            # Message status may be 'success', 'error', 'running', 'queued'.
            if message_data['status'] == 'error':
                raise Exception(message_data['text'])

            if message_data['status'] == 'success':
                break

    elif data['results'] is None:
        raise Exception(data['message'])

    # 'results' is the URL to the search results
    res = requests.get(data['results'])
    dt = time.monotonic() - start

    # response is JSON formatted
    return data['results'], dt, res.json()


def summarize(results_url: str, dt: float, data: Any) -> None:
    count_by_survey = []
    for survey in set([row['source'] for row in data['data']]):
        n = len([row for row in data['data']
                 if row['source'] == survey])
        count_by_survey.append(f'  - {n} {survey}\n')

    print(f'''
Job ID: {data['job_id']}
Results: {results_url}
Elapsed time: {dt:.1f} s
Count: {data['count']}''')

    if len(count_by_survey) > 0:
        print(''.join(count_by_survey))


if __name__ == '__main__':
    args = parse_args()

    print(f'''
CATCH APIs Query

Base URL: {args.url}
Target: {args.target}
Cached results allowed? {args.cached}
''')

    results_url, dt, data = query(args)
    summarize(results_url, dt, data)
