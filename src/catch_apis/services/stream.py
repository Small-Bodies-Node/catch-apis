"""Message stream data."""

from typing import Iterator
import time

from ..config import ENV
from .queue import RedisConnection


def messages(timeout: int = 0) -> Iterator[str]:
    """Iterator for all CATCH-APIs task messages.

    Listens to redis task messaging stream, prints the messages.


    Parameters
    ----------
    timeout : int, optional
        Number of seconds to loop before timing out.  If 0, then only time out
        after ENV.STREAM_TIMEOUT seconds of continuous keep alive messages.

    """

    redis: RedisConnection = RedisConnection()

    last: bytes = b'0'
    start_time: float = time.monotonic()
    wait: int = 3  # seconds between keep alive messages
    count: int = 0  # number of consecutive keep alive messages
    while True:
        message = redis.xread({ENV.REDIS_TASK_MESSAGES: last},
                              count=1, block=wait * 1000)

        if timeout > 0 and (time.monotonic() - start_time) > timeout:
            break

        if len(message) == 0:
            count += 1
            if count > (ENV.STREAM_TIMEOUT // wait):
                yield ': timeout\n\n'
                return
            else:
                yield ': stayin\' alive\n\n'
                continue

        content: bytes
        last, content = message[0][1][0]
        data: str = content.get(b'data', b'').decode()
        if data != '':
            count = 0
            yield f'data: {data}\n\n'
