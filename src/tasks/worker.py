"""
    Script to launch a new rq worker listening to JOBS queue
"""

from typing import List
from redis import from_url, Redis
from rq import Worker, Queue, Connection
from env import ENV

from tasks import RQueues

subscribed_queues: List[str] = [RQueues.JOBS]

redis_url: str = 'redis://localhost:'+str(ENV.REDIS_PORT)

conn: Redis = from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker: Worker = Worker(map(Queue, subscribed_queues))
        worker.work()
