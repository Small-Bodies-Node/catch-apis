from routes import init_api_routes
from flask import *

app = Flask(__name__)

init_api_routes(app)


@app.route("/test")
def index():
    return "Hello World!"


if __name__ == "__main__":
    app.run(port=5001)
