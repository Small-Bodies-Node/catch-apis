#!/usr/bin/env python3
"""
    Script to launch a new rq worker listening to JOBS queue.
"""

from rq import Worker, Queue, Connection
from catch_apis.services.queue import RQueues, RedisConnection


if __name__ == '__main__':
    with Connection(RedisConnection()):
        worker: Worker = Worker(map(Queue, [RQueues.JOBS]))
        worker.work()
