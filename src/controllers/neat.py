"""
    NEAT Module
    Creates RestPlus namespace for NEAT controller.
"""

import logging
import uuid
from typing import Dict, List, Union
import flask_restplus as FRP
from flask import request
import models
import services
from util import jsonify_output

API: FRP.Namespace = models.neat.App.api

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/query")
class NEATQuery(FRP.Resource):
    """Controller class for NEAT queries."""

    @API.doc('--neat/query--')
    @API.param(
        'sessionid', _in='query',
        description='User session ID.'
    )
    @API.param(
        'designation', _in='query',
        description='Search for this object by designation.'
    )
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'NEATQuery') -> Dict[str, Union[str, int]]:
        """Query NEAT."""

        # Extract params from URL
        sessionid: str = request.args.get('sessionid', uuid.uuid4(), str)
        designation: str = request.args.get('designation', 0, str)

        print("sessionid: "+sessionid)

        # Pass params to data-provider-service
        queryid: int = services.neat.query(sessionid, designation)

        return {
            'sessionid': sessionid,
            'queryid': queryid,
            'designation': designation
        }


@API.route("/caught/<string:sessionid>/<int:queryid>")
class NEATCaught(FRP.Resource):
    """Controller class for NEAT caught objects."""

    @API.doc('--neat/caught/sessionid/queryid--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(models.neat.App.caught)
    # def get(self: 'NEATCaught', sessionid: str, queryid: int) -> Dict[str, Union[Dict[str, Union[str, int, float]], str, int]]:
    def get(self: 'NEATCaught', sessionid: str, queryid: int) -> Dict[str, Union[List[dict], str, int]]:
        """Query NEAT caught objects by session and query ID."""

        data: List[dict] = services.neat.caught(sessionid, queryid)

        return {
            'data': data,
            'sessionid': sessionid,
            'queryid': queryid,
            'total': len(data)
        }


@API.route("/caught/labels")
class NEATCaughtLabels(FRP.Resource):
    """Controller for NEAT caught object column labels."""

    @API.doc('--neat/caught/labels--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'NEATCaughtLabels') -> Dict[str, Dict[str, str]]:
        """NEAT caught object table labels."""
        data: Dict[str, Dict[str, str]] = (
            services.neat.column_labels('/caught'))
        return data
