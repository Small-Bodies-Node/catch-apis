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
            description='text message for user'
        ),
        'queued': fields.Boolean(
            description=('true if a search has been queued, '
                         'false if the results are ready')
        ),
        'query': fields.String(
            description="user's inputs"
        ),
        'job_id': fields.String(
            description='unique job ID for retrieving results'
        ),
        'results': fields.String(
            description='URL from which to retrieve results'
        )
    })

    target_name_model: Model = api.model('QueryTarget', {
        'name': fields.String(description='input name'),
        'type': fields.String(
            description=('target type: asteroid, comet, '
                         'interstellar object, or unknown')
        ),
        'match': fields.String(
            description='target type identification was based on this string'
        ),
        'valid': fields.Boolean(
            description='false if unknown, otherwise true'
        )
    })

    # Todo: matches is supposed to return a list of dictionaries
    # Todo: ... I tried using fields.List and fields.Nested, but got opaque errors
    # Todo: ... For now, fields.String seems to work
    search_name_model: Model = api.model('SearchTarget', {
        'name': fields.String(description='input name'),
        'matches': fields.String(
            description='list of best matches'
        )

    })
