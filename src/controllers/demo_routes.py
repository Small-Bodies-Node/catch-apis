"""
Demo Routes Module
Just a bunch of simple routes that you can reference/copy to start developing new routes
"""

import logging
import typing

from flask import jsonify, request
import flask.wrappers as FLW
import flask_restplus as FRP


API = FRP.Namespace(
    name='Demo',
    path="/demo",
    description='Root route; used for demo-ing the API is up and running, etc.'
)

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/")
class DemoRoutes(FRP.Resource):
    """Controller class for demo-routes"""

    @API.doc('--demo--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'DemoRoutes') -> typing.Any:
        '''Returns trivial json object'''

        # Return a trivial json
        res: FLW.Response = jsonify(
            {
                "message": "This is the demo GET route which doesn't do much."
            }
        )
        res.status_code = 200
        return res

    @API.doc('--demo--')
    @API.param('example', description='Place a string here as an example of a POST request', _in='body')
    @FRP.cors.crossdomain(origin='*')
    def post(self: 'DemoRoutes') -> FLW.Response:
        """Returns trivial json object"""

        # Demo logging
        logger.debug('"DEMO POST DEBUG"')
        logger.info('"DEMO POST INFO"')
        logger.warning('"DEMO POST WARNING"')
        logger.critical('"DEMO POST CRITICAL"')

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
