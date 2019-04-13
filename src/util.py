from typing import Callable
from functools import wraps
from flask import jsonify
from flask.wrappers import Response


def jsonify_output(f) -> Callable:
    @wraps(f)
    def jsonified(*args, **kwargs) -> Response:
        res: Response = jsonify(f(*args, **kwargs))
        res.status_code = 200
        return res
    return jsonified
