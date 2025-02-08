"""Entry point to Flask-Connexion API"""

import logging

import connexion
from connexion.middleware import MiddlewarePosition
from starlette.middleware.cors import CORSMiddleware
from flask import Response

from catch_apis.config.env import ENV
from . import __version__ as version
from .config import allowed_sources, get_logger
from .services.stream import message_stream_service

logger: logging.Logger = get_logger()
app = connexion.FlaskApp(__name__, specification_dir="api/")

app.add_middleware(
    CORSMiddleware,
    position=MiddlewarePosition.BEFORE_EXCEPTION,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_api(
    "openapi.yaml",
    arguments={
        "version": version,
        "base_href": ENV.BASE_HREF,
        "sources": allowed_sources,
        "test_env": ENV.DEPLOYMENT_TIER == "TEST",
    },
)
application = app.app

# openapi does not support SSE; define /stream here


@application.route("/stream")
def stream() -> Response:
    """Shared task messaging stream."""

    return Response(
        message_stream_service(),
        mimetype="text/event-stream",
        headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Keep-Alive": "timeout=55",
        },
    )


if __name__ == "__main__":  # pragma: no cover
    # for development
    logger.info("Running " + ENV.APP_NAME)
    app.run("catch_apis.app:app", host=ENV.API_HOST, port=ENV.API_PORT)
