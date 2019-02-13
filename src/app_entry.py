"""Entry file into the flask API server."""

# from typing import Any
from typing import Any

from flask import Flask, request, jsonify

# from flask2 import jsonify2
from flask.wrappers import Response  # , Request
from routes import init_api_routes
from middleware import moving_object_search

APP: Any = Flask(__name__)
init_api_routes(APP)


@APP.route("/get-test")
def test1() -> str:
    '>>> Just a get test'
    return "Hello World!"


@APP.route("/post-test", methods=['POST'])
def test2() -> Response:
    '>>> Just a post test'
    content = request.get_json(silent=True)
    print(">>>>" + 'Just a post test')
    # print(content+"xxx")
    d: str = '' * 2
    print(d)
    # a: int = 1.2
    return jsonify(content)


@APP.route("/moving-object-search")
def test3() -> Response:
    '>>> Just a db-query test'
    objid: str = request.args.get('objid', 'xxxxx', str)
    start: int = request.args.get('start', 0, int)
    end: int = request.args.get('end', 50, int)
    print(">>>> " + str(start))
    print(">>>> " + str(end))
    moving_object_search_result: Response = moving_object_search(
        objid, start, end)
    return moving_object_search_result


if __name__ == "__main__":
    APP.run(port=5001)
