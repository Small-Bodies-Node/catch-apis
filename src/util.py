from typing import Callable
from functools import wraps
from flask import jsonify
from flask.wrappers import Response
from flask_restplus import fields


def jsonify_output(f) -> Callable:
    @wraps(f)
    def jsonified(*args, **kwargs) -> Response:
        res: Response = jsonify(f(*args, **kwargs))
        res.status_code = 200
        return res
    return jsonified


class FormattedStringOrNone(fields.FormattedString):
    def output(self, key, obj, **kwargs):
        try:
            return super().output(key, obj, **kwargs)
        except (KeyError, AttributeError):
            return None
