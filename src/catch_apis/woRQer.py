"""
    Script to launch a new rq worker listening to JOBS queue.
"""

from rq import Worker as WoRQer, Queue, Connection

from .config import ENV
from .services.queue import RedisConnection

if __name__ == "__main__":
    with Connection(RedisConnection()):
        queue_name = ENV.REDIS_JOBS
        woRQer: WoRQer = WoRQer(map(Queue, [queue_name]), default_worker_ttl=1000)
        woRQer.work()
