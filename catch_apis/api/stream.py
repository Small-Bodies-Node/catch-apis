import json
from typing import Dict, Iterator

from ..services.queue import RQueues, RedisConnection
from ..env import ENV


def messages() -> Iterator[str]:
    """Iterator for all CATCH-APIs task messages.

    Listens to redis task messaging stream, prints the messages.

    """

    redis: RedisConnection = RedisConnection()

    last: bytes = b'0'
    wait: int = 3  # seconds between keep alive messages
    count: int = 0  # number of consecutive keep alive messages
    while True:
        message = redis.xread({RQueues.TASK_MESSAGES: last},
                              count=1, block=wait * 1000)
        if len(message) == 0:
            count += 1
            if count > (ENV.STREAM_TIMEOUT // wait):
                yield ': timeout\n'
                return
            else:
                yield ': stayin\' alive\n'
                continue

        content: bytes
        last, content = message[0][1][0]
        data: str = content.get(b'data', b'').decode()
        if data != '':
            count = 0
            yield f'data: {data}\n'
