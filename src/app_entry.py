"""Entry file into the Flask-REST API server."""

from flask import Flask, wrappers as FLW, jsonify
# from werkzeug.contrib.fixers import ProxyFix <-- deprecated
from werkzeug.middleware.proxy_fix import ProxyFix


#import flask_monitoringdashboard as dashboard
from logging_setup import logger    # Must come BEFORE controllers import
from controllers import default_error_handler, blueprint as rest_plus_blueprint
from env import ENV, EDeploymentTier

# Choose port to run app locally based on deployment tier
if ENV.DEPLOYMENT_TIER == EDeploymentTier.PROD:
    PORT = 5000
elif ENV.DEPLOYMENT_TIER == EDeploymentTier.STAGE:
    PORT = 5001
elif ENV.DEPLOYMENT_TIER == EDeploymentTier.SANDBOX:
    PORT = 5002
elif ENV.DEPLOYMENT_TIER == EDeploymentTier.LOCAL:
    PORT = 5003
else:
    raise Exception('Unrecognized DEPLOYMENT_TIER')

# Init Flask App and associate it with RestPlus controllers
flask_app: Flask = Flask(__name__)
flask_app.url_map.strict_slashes = False

# Define sth at flask's bare root; must come BEFORE associating flask app with restplus


@flask_app.route('/')
def bare_root() -> FLW.Response:
    """Message for bare-api route"""
    res: FLW.Response = jsonify(
        {
            "message":
            """
                This is the CATCH API's root route.
                Not much here. Go to {}/docs for swagger documentation.
            """.format(rest_plus_blueprint.url_prefix)
        }
    )
    res.status_code = 200
    return res


# Associate flask app with flask_restplus configurations via blueprint
flask_app.register_blueprint(rest_plus_blueprint)

# Configure and associate monitoring dashboard
# dashboard.config.init_from(envvar=ENV.DASHBOARD_CONFIG)
# dashboard.bind(flask_app)

# Required for custom error handler; see: https://stackoverflow.com/a/36575875/9730910
flask_app.config['TRAP_HTTP_EXCEPTIONS'] = True
flask_app.register_error_handler(Exception, default_error_handler)

# This is required to serve swagger through https;
# Source: https://github.com/noirbizarre/flask-restplus/issues/54#issuecomment-143436291
flask_app.wsgi_app = ProxyFix(flask_app.wsgi_app)  # type: ignore

# Required to trim whitespaces in templates
flask_app.jinja_env.trim_blocks = True
flask_app.jinja_env.lstrip_blocks = True

# Opens swagger routes by default:
flask_app.config.SWAGGER_UI_DOC_EXPANSION = 'list'  # type: ignore

# Start app
if __name__ == "__main__":
    flask_app.run(port=PORT)
    logger.info("<><><> STARTING APP <><><>")
