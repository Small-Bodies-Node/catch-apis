"""
    Gunicorn workers-config file
    Logic to decide how many workers to launch for flask app
"""

import multiprocessing
from .env import ENV

workers: int = ENV.GUNICORN_FLASK_INSTANCES

if workers == -1:
    workers = multiprocessing.cpu_count() * 2
