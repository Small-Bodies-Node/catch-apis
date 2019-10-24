"""
Controller for survey searches.
"""

import logging
import uuid
from typing import Dict, Union

import flask_restplus as FRP
from flask import Response, jsonify

from models.caught import App
import services.caught as service
from util import jsonify_output

API: FRP.Namespace = App.api

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/<string:job_id>")
class Caught(FRP.Resource):
    """Controller class for caught moving target data."""

    @API.doc('--caught/--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'Caught', job_id: Union[str, uuid.UUID]) -> Response:
        """Caught moving target data."""

        # validate job_id format
        job_id = uuid.UUID(str(job_id), version=4)

        # retrieve data
        data: dict = service.caught(job_id)

        response: Response = jsonify({
            "count": len(data),
            "job_id": job_id.hex,
            "data": FRP.marshal(data, App.caught_data)
        })
        response.status_code = 200
        return response


@API.route("/labels")
class CaughtLabels(FRP.Resource):
    """Controller for caught moving object table labels."""

    @API.doc('--caught/labels--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'CaughtLabels') -> Dict[str, Dict[str, str]]:
        """Caught moving object table labels."""
        data: Dict[str, Dict[str, str]] = (
            service.column_labels('/'))
        return data
