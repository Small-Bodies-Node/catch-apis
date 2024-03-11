"""Entry point to Flask-Connexion API"""

import logging
from typing import Iterator

import connexion
from flask import Response

from . import __version__
from .config import allowed_sources, get_logger, ENV
from .services.queue import RedisConnection
from .config.env import ENV


def messages() -> Iterator[str]:
    """Iterator for all CATCH-APIs task messages.

    Listens to redis task messaging stream, prints the messages.

    """

    redis: RedisConnection = RedisConnection()

    last: bytes = b'0'
    wait: int = 3  # seconds between keep alive messages
    count: int = 0  # number of consecutive keep alive messages
    while True:
        message = redis.xread({ENV.REDIS_TASK_MESSAGES: last},
                              count=1, block=wait * 1000)
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


logger: logging.Logger = get_logger()
app = connexion.FlaskApp(__name__, specification_dir="api/")
app.add_api(
    "openapi.yaml",
    arguments={
        "version": __version__,
        "base_href": ENV.BASE_HREF,
        "sources": allowed_sources,
    },
)
application = app.app

# openapi does not support SSE; define /stream here


@application.route("/stream")
def stream() -> Response:
    """Shared task messaging stream."""

    return Response(
        messages(),
        mimetype="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=55",
        },
    )

if __name__ == "__main__":
    logger.info("Running " + ENV.APP_NAME)
    app.run("catch_apis.app:app", port=ENV.API_PORT)
