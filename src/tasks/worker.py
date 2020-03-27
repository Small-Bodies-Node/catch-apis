from tasks import RQueues
from env import ENV
from rq import Worker, Queue, Connection
from redis import from_url, Redis
from typing import List
"""
    Script to launch a new rq worker listening to START_JOBS queue
"""

subscribed_queues: List[str] = [RQueues.START_JOBS]

redis_url: str = 'redis://localhost:'+str(ENV.REDIS_PORT)

conn: Redis = from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker: Worker = Worker(map(Queue, subscribed_queues))
        worker.work()
