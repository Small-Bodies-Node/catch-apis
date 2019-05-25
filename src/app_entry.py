"""Entry file into the Flask-REST API server."""

import os
import flask
import flask.wrappers as FLW
from werkzeug.contrib.fixers import ProxyFix

import flask_monitoringdashboard as dashboard
from dotenv import load_dotenv
from logging_setup import logger    # Must come BEFORE controllers import
from controllers import default_error_handler, blueprint as rest_plus_blueprint

# Load .env variables
load_dotenv(verbose=True)

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


# Associate flask app with flask_restplus configurations via blueprint
flask_app.register_blueprint(rest_plus_blueprint)

DASHBOARD_CONFIG = os.getenv("DASHBOARD_CONFIG")
dashboard.config.init_from(envvar='DASHBOARD_CONFIG')
dashboard.bind(flask_app)


# Required for custom error handler; see: https://stackoverflow.com/a/36575875/9730910
flask_app.config['TRAP_HTTP_EXCEPTIONS'] = True
flask_app.register_error_handler(Exception, default_error_handler)

# This is required to serve swagger through https; source: https://github.com/noirbizarre/flask-restplus/issues/54#issuecomment-143436291
flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app)  # type: ignore

# Required to trim whitespaces in templates
flask_app.jinja_env.trim_blocks = True
flask_app.jinja_env.lstrip_blocks = True

# Opens swagger routes by default:
flask_app.config.SWAGGER_UI_DOC_EXPANSION = 'list'  # type: ignore

# Start app
if __name__ == "__main__":
    flask_app.run(port=5001)
    logger.info("<><><> STARTING APP <><><>")
