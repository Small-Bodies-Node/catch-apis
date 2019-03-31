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
                "message":
                """
                        This is the demo GET route which doesn't do much.
                    """
            }
        )
        res.status_code = 200
        return render_template('temp.html', title='Home')
        # return render_template
        # return res

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


# @API.route("/template")
# class DemoTemplates(FRP.Resource):
#     '''Controller class for demo-routes with templates'''

#     @API.doc('--template--')
#     @FRP.cors.crossdomain(origin='*')
#     def get(self: 'DemoTemplates') -> typing.Any:
#         '''Returns simple template'''

#         # Return a trivial template
#         return render_template('demo-template.html', title='Demo Template'), 200


# @API.route("/plotly")
# class DemoPlotly(FRP.Resource):
#     '''Controller class for demo-scatter plot using plotly'''

#     @API.doc('--scatter--')
#     @FRP.cors.crossdomain(origin='*')
#     def get(self: 'DemoTemplates') -> typing.Any:
#         '''Returns simple scatter plot'''
#         count = 500
#         xScale = np.linspace(0, 100, count)
#         yScale = np.random.randn(count)

#         # Create a trace
#         trace = go.Scatter(
#             x=xScale,
#             y=yScale
#         )

#         data = [trace]
#         graphJSON: str = json.dumps(data, cls=plotly.utils.PlotlyJSONEncoder)

#         return render_template('plotly-scatter-example.html', graphJSON=graphJSON), 200
