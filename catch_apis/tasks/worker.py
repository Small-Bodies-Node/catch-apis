"""
    Script to launch a new rq worker listening to JOBS queue
"""

from rq import Worker, Queue, Connection
from ..services.queue import RQueues, RedisConnection


if __name__ == '__main__':
    with Connection(RedisConnection()):
        worker: Worker = Worker(map(Queue, [RQueues.JOBS]))
        worker.work()
