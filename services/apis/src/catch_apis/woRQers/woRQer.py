"""
    Script to launch a new rq worker listening to JOBS queue.
"""

import os
from rq import Worker as WoRQer, Queue, Connection
from redis import StrictRedis

connect = StrictRedis(host=os.getenv('REDIS_HOST', 'redis-server'))
with Connection(connect):
    queue_name = os.getenv('REDIS_JOBS', 'JOBS_DEV')
    woRQer: WoRQer = WoRQer(map(Queue, [queue_name]), default_worker_ttl=1000)
    woRQer.work()
