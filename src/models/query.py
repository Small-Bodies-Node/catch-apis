"""
/query route namespace and data models.
"""

from flask_restplus import Namespace


class App:
    """/query route namespace and return data models."""
    api: Namespace = Namespace(
        'Catch moving targets',
        path="/query"
    )
