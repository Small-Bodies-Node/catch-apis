"""Entry file into the Flask-REST API server."""

from typing import Any
from flask import Flask
from controllers import rest_plus_apis

# Init Flask App
flask_app: Any = Flask(__name__)

# Associate Flask App with RestPlus Configurations
rest_plus_apis.init_app(flask_app)


if __name__ == "__main__":
    flask_app.run(port=5001)
