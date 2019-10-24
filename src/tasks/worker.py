"""
    Script to launch a new rq worker listening to START_JOBS queue
"""

from typing import List
from redis import from_url, Redis
from rq import Worker, Queue, Connection
from env import ENV

from tasks import RQueues

subscribed_queues: List[str] = [RQueues.START_JOBS]

redis_url: str = 'redis://localhost:'+str(ENV.REDIS_PORT)

print(">>> "+redis_url)

conn: Redis = from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker: Worker = Worker(map(Queue, subscribed_queues))
        worker.work()
