"""Entry file into the Flask-REST API server."""

from typing import Any
from flask import Flask
from controllers import REST_PLUS_APIS, default_error_handler

# Init Flask App
flask_app: Any = Flask(__name__)

# Associate Flask App with RestPlus Configurations
REST_PLUS_APIS.init_app(flask_app)

# Required for custom error handler; see: https://stackoverflow.com/a/36575875/9730910
flask_app.config['TRAP_HTTP_EXCEPTIONS'] = True
flask_app.register_error_handler(Exception, default_error_handler)

if __name__ == "__main__":
    flask_app.run(port=5001)
