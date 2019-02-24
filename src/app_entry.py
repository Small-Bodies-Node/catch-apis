"""Entry file into the Flask-REST API server."""

import flask
import flask.wrappers as FLW

from logging_setup import logger    # Must come BEFORE controllers import
from controllers import REST_PLUS_APIS, default_error_handler, blueprint as mybp

# Init Flask App and associate it with RestPlus controllers
flask_app: flask.Flask = flask.Flask(__name__)
flask_app.url_map.strict_slashes = False

# Define sth at flask's bare root; must come BEFORE associateing flask app with restplus
@flask_app.route('/')
def bare_root() -> FLW.Response:
    """Message for bare-api route"""
    res: FLW.Response = flask.jsonify(
        {
            "message":
            """
                This is the CATCH API's root route.
                Not much here. Go to /docs for swagger documentation.
            """
        }
    )
    res.status_code = 200
    return res


# Associate flask app with flask_restplus configurations
# REST_PLUS_APIS.init_app(flask_app)
flask_app.register_blueprint(mybp)

# Required for custom error handler; see: https://stackoverflow.com/a/36575875/9730910
flask_app.config['TRAP_HTTP_EXCEPTIONS'] = True
flask_app.register_error_handler(Exception, default_error_handler)

# Start app
if __name__ == "__main__":
    flask_app.run(port=5001)
    logger.info("<><><> STARTING APP <><><>")
