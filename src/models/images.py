"""
/images route namespace and data model.
"""

from flask_restplus import Namespace


class App:
    """/query route namespace and return data models."""
    api: Namespace = Namespace(
        'Image service',
        path="/images"
    )
