"""
Script to launch a new rq worker listening to JOBS queue.
"""

from rq import Worker as WoRQer

from .services.queue import JobsQueue


def run(burst: bool = False):
    """Set burst to True and the worker will quit when the queue is empty."""
    queue = JobsQueue()
    woRQer = WoRQer(queue, worker_ttl=1000)
    woRQer.work(burst=burst)


if __name__ == "__main__":
    run()
