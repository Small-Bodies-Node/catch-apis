"""
/query route namespace and data models.
"""

from flask_restplus import Namespace, Model, fields


class App:
    """/query route namespace and return data models."""
    api: Namespace = Namespace(
        'Catch moving targets',
        path="/query"
    )

    query_model: Model = api.model('QueryMoving', {
        'message': fields.String(
            description='Text message for user'
        ),
        'query': fields.String(
            description="User's inputs"
        ),
        'job_id': fields.String(
            description='Unique job ID for retrieving results'
        ),
        'results': fields.String(
            description='URL from which to retrieve results'
        )
    })
