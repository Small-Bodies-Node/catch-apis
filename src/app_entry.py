"""Entry file into the Flask-REST API server."""

import os
import logging
import logging.config
from logging import Logger
from flask import Flask

# Setup logging throughout application
logging_conf_path: str = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..', 'logging.ini'))
logging.config.fileConfig(logging_conf_path, disable_existing_loggers=False)
logger: Logger = logging.getLogger(__name__)

# Init Flask App and associate it with RestPlus controllers
from controllers import REST_PLUS_APIS, default_error_handler
flask_app: Flask = Flask(__name__)
REST_PLUS_APIS.init_app(flask_app)

# Required for custom error handler; see: https://stackoverflow.com/a/36575875/9730910
flask_app.config['TRAP_HTTP_EXCEPTIONS'] = True
flask_app.register_error_handler(Exception, default_error_handler)

if __name__ == "__main__":
    flask_app.run(port=5001)
    logger.info("<><><> STARTING APP <><><>")
