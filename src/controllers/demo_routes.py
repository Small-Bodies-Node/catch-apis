"""
Test Routes Module
"""

import logging
from flask import request, jsonify
import flask.wrappers as FLW
import flask_restplus as FRP

API = FRP.Namespace(
    name='Test',
    path="/test",
    description='Root route; used for testing the API is up and running, etc.'
)

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/")
class TestRoutes(FRP.Resource):
    """Controller class for test-routes"""

    @API.doc('--test--')
    def get(self: 'TestRoutes') -> FLW.Response:
        """Returns trivial json object"""

        # Return a trivial json
        res: FLW.Response = jsonify(
            {
                "message":
                """
                    This is the test GET route which doesn't do much.
                """
            }
        )
        res.status_code = 200
        return res

    @API.doc('--test--')
    def post(self: 'TestRoutes') -> FLW.Response:
        """Returns trivial json object"""

        # Test logging
        logger.debug('"TEST POST DEBUG"')
        logger.info('"TEST POST INFO"')
        logger.warning('"TEST POST WARNING"')
        logger.critical('"TEST POST CRITICAL"')

        # Extract data from POST body
        data = request.json

        # Return posted data as part of simple POST-cycle demo
        res: FLW.Response = jsonify(
            {
                "message":
                """
                    Wow! This is the data you posted!
                """,
                "posted-data": data
            }
        )
        res.status_code = 200
        return res
