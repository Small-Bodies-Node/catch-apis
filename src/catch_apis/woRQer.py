"""
Script to launch a new rq worker listening to JOBS queue.
"""

from rq import Worker as WoRQer, Connection

from .services.queue import RedisConnection, JobsQueue


def run(burst: bool = False):
    """Set burst to True and the worker will quit when the queue is empty."""
    with Connection(RedisConnection()):
        queue = JobsQueue()
        woRQer = WoRQer(queue, default_worker_ttl=1000)
        woRQer.work(burst=burst)


if __name__ == "__main__":
    run()
