"""
    Script to launch a new rq worker listening to JOBS queue.
"""

from rq import Worker as WoRQer, Queue, Connection

from catch_apis.config.env import ENV
from .services.queue import RedisConnection


def run(burst: bool = False):
    """Set burst to True and the worker will quit when the queue is empty."""
    with Connection(RedisConnection()):
        queue_name = ENV.REDIS_JOBS
        woRQer: WoRQer = WoRQer(map(Queue, [queue_name]), default_worker_ttl=1000)
        woRQer.work(burst=burst)


if __name__ == "__main__":
    run()
