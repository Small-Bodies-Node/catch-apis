"""Entry file into the flask API server."""

from flask import Flask, request, jsonify
from routes import init_api_routes


APP = Flask(__name__)
init_api_routes(APP)


@APP.route("/get-test")
def test1():
    return "Hello World!"


@APP.route("/post-test", methods=['POST'])
def test2():
    content = request.get_json(silent=True)
    print(">>>>")
    # print(content+"xxx")
    return jsonify(content)


if __name__ == "__main__":
    APP.run(port=5001)
