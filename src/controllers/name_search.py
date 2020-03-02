
"""
Name-Search Controller
Routes for submitting
"""


import logging
from typing import Dict, Union, Any, List
import flask_restplus as FRP
from flask import request, wrappers as FLW, jsonify, Response
from models.query import App
from services.name_search import name_search
from util import jsonify_output
import flask.wrappers as FLW

API: FRP.Namespace = App.api
logger: logging.Logger = logging.getLogger(__name__)


@API.route("/name")
class NameSearch(FRP.Resource):
    """Controller class for testing target names."""

    @API.doc('--search/name--')
    @API.param(
        'name', _in='query',
        description='Target name to search for.'
    )
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'NameSearch') -> FLW.Response:
        """Search moving target name."""

        name: str = request.args.get('name', '', str)
        top_matches: dict = name_search(name)
        res: FLW.Response = jsonify(
            {
                "name": name,
                "matches": top_matches
            }
        )
        res.status_code = 200
        return res
