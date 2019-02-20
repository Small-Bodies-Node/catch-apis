"""
Test Routes Module
"""

from typing import Any, Tuple
from flask import request, jsonify
from flask.wrappers import Response  # , Request
from flask_restplus import Namespace, Resource, fields
from services import DATA_PROVIDER

API = Namespace('test',
                description='Used for testing the API is up and running')


@API.route("")
class MovingObjectSearch(Resource):
    """Controller class for test-routes"""

    @API.doc('--test--')
    def get(self: Any) -> Response:
        """Returns moving-object-search requests"""

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "message": "It worked!!!"
            }
        )
        print("Working?")
        return res
