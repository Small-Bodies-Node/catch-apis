"""
Generic functions for catch-apis.
"""
from typing import Callable
from functools import wraps
from flask import jsonify
from flask.wrappers import Response
from flask_restplus import fields


def jsonify_output(f) -> Callable:
    """Function wrapper to transform output into HTTP response."""
    @wraps(f)
    def jsonified(*args, **kwargs) -> Response:
        """Returns data with successful HTTP response."""
        res: Response = jsonify(f(*args, **kwargs))
        res.status_code = 200
        return res
    return jsonified


class FormattedStringOrNone(fields.FormattedString):
    """Data marshalling: return formatted string or None."""

    def output(self, key, obj, **kwargs):
        """Formatted string or None."""
        try:
            return super().output(key, obj, **kwargs)
        except (KeyError, AttributeError):
            return None
