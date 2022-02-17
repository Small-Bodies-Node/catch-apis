"""
Entry point to Flask-Connexion API
"""

from typing import Tuple
from connexion import FlaskApp
from flask_cors import CORS
from flask import Response
from ..config.env import ENV
from .. import services
from .stream import messages
from ..config.logging import get_logger
from ..config.exceptions import CatchException, CatchApisException

app = FlaskApp(__name__, options={})
app.add_api('openapi.yaml', base_path=ENV.BASE_HREF, validate_responses=True)
CORS(app.app)
application = app.app

# openapi does not support SSE; define /stream here


@application.route('/stream')
def stream() -> Response:
    """Shared task messaging stream."""

    return Response(
        messages(),
        mimetype='text/event-stream',
        headers={
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Keep-Alive': 'timeout=55'
        }
    )


@application.teardown_appcontext
def shutdown_session(exception: Exception = None) -> None:
    """ Boilerplate connexion code """
    services.database_provider.db_session.remove()


@application.errorhandler(CatchException)
def handle_catch_error(error: Exception) -> Tuple[str, int]:
    """Log errors."""
    get_logger().exception('CATCH error.')
    return str(error), getattr(error, 'code', 500)


@application.errorhandler(CatchApisException)
def handle_catch_apis_error(error: Exception) -> Tuple[str, int]:
    """Log errors."""
    get_logger().exception('CATCH APIs error.')
    return str(error), getattr(error, 'code', 500)


@application.errorhandler(Exception)
def handle_other_error(error: Exception) -> Tuple[str, int]:
    """Log errors."""
    get_logger().exception('An error occurred.')
    return ('Unexpected error.  Please report if the problem persists.',
            getattr(error, 'code', 500))


if __name__ == '__main__':
    app.run(port=ENV.API_PORT, use_reloader=False, threaded=True)
