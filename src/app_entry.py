"""Entry file into the flask API server."""

from flask import Flask, request, jsonify
from routes import init_api_routes
from middleware import moving_object_search

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


@APP.route("/moving-object-search")
def test3():
    objid: str = str(request.args.get('objid'))
    start: int = int(request.args.get('start'))
    end: int = int(request.args.get('end'))
    print(">>>> "+str(start))
    print(">>>> "+str(end))
    x = moving_object_search(objid, start, end)
    return x
    # return jsonify(x)


if __name__ == "__main__":
    APP.run(port=5001)
