"""
Generic functions for catch-apis.
"""
from typing import Callable, Any
from functools import wraps
from flask import jsonify
from flask.wrappers import Response
from flask_restplus import fields


def jsonify_output(f: Callable) -> Callable:
    """Function wrapper to transform output into HTTP response."""
    @wraps(f)
    def jsonified(*args: Any, **kwargs: Any) -> Response:
        """Returns data with successful HTTP response."""
        res: Response = jsonify(f(*args, **kwargs))
        res.status_code = 200
        return res
    return jsonified


class FormattedStringOrNone(fields.FormattedString):
    """Data marshalling: return formatted string or None."""

    def output(self: 'FormattedStringOrNone', key: Any, obj: Any, **kwargs: Any) -> Any:
        """Formatted string or None."""
        try:
            super().output(key, obj, **kwargs)
            return super().output(key, obj, **kwargs)
        except (KeyError, AttributeError):
            return None


def desg_to_prefix(desg: str) -> Any:
    """Convert small body designation to file prefix."""
    return (desg.replace('/', '').replace(' ', '')
            .replace('(', '_').replace(')', '_'))
