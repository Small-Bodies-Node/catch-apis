""" """
from redis import StrictRedis
from rq import Queue
from ..config.env import ENV


# class RQueues:
#     """Redis queue names."""
#     JOBS = "JOBS-"+str(ENV.DEPLOYMENT_TIER)
#     TASK_MESSAGES = "TASK_MESSAGES-"+str(ENV.DEPLOYMENT_TIER)


class RedisConnection(StrictRedis):
    """Connect to Redis."""

    def __init__(self):
        super(RedisConnection, self).__init__(
            host=ENV.REDIS_HOST, port=ENV.REDIS_PORT)


class JobsQueue(Queue):
    """Jobs queue.

    Examples
    --------
    >>> queue = JobsQueue()
    >>> print(len(queue.jobs), 'jobs queued')
    >>> print('Queue filled?', queue.full)
    >>> queue.enqueue(func, *args)

    """

    def __init__(self):
        super().__init__(
            # RQueues.JOBS, connection=RedisConnection()
            ENV.REDIS_JOBS, connection=RedisConnection()
        )

    @property
    def full(self):
        return len(self) >= ENV.REDIS_MAX_QUEUE_SIZE
