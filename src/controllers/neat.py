"""
Demo Routes Module
Just a bunch of simple routes that you can reference/copy to start developing new routes
"""

import logging
import typing
import json

from flask import Flask, jsonify, render_template, request
import flask.wrappers as FLW
import flask_restplus as FRP

# import plotly
# import plotly.graph_objs as go
# import numpy as np


API = FRP.Namespace(
    name='NEAT',
    path="/neat",
    description='NEAT survey route.'
)

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/")
class NEATRoutes(FRP.Resource):
    """Controller class for NEAT routes"""

    @API.doc('--neat--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'NEATRoutes') -> typing.Any:
        '''Returns trivial json object'''

        # Return a trivial json
        res: FLW.Response = jsonify(
            {
                "message": "You just got NEAT."
            }
        )
        res.status_code = 200
        return res

    @API.doc('--demo--')
    @API.param('example', description='Example of a POST request', _in='body')
    @FRP.cors.crossdomain(origin='*')
    def post(self: 'NEATRoutes') -> FLW.Response:
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
                    NEAT survey results.
                """,
                "posted-data": data
            }
        )
        res.status_code = 200
        return res
