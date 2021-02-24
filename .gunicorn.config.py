"""
    Gunicorn workers-config file
    Logic to decide how many workers to launch based on .env variable `LIVE_GUNICORN_INSTANCES`
    NOTE: some gunicorn params (e.g. --name) don't seem to work from here so must be called from the command line
"""

import multiprocessing
from catch_apis.env import ENV

workers: int = ENV.LIVE_GUNICORN_INSTANCES

if ENV.LIVE_GUNICORN_INSTANCES == -1:
    workers = multiprocessing.cpu_count() * 2
