"""
Controller for survey searches.
"""

import logging
import uuid
from typing import Dict, Union

import flask_restplus as FRP
from flask import jsonify, Response

from models.caught import App, COLUMN_LABELS
import services.caught as service
from util import jsonify_output

API: FRP.Namespace = App.api

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/<string:job_id>")
class Caught(FRP.Resource):
    """Controller class for caught moving target data."""

    @API.doc('--caught/--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(App.caught_model)
    def get(self: 'Caught', job_id: Union[str, uuid.UUID]) -> Dict[str, Union[str, dict, int]]:
        """Caught moving target data."""

        # validate job_id format
        job_id = uuid.UUID(str(job_id), version=4)

        data: dict = service.caught(job_id)
        payload: Dict[str, Union[str, dict, int]] = {
            "count": len(data),
            "job_id": job_id.hex,
            "data": data
        }
        return payload


@API.route("/labels")
class CaughtLabels(FRP.Resource):
    """Controller for caught moving object table labels."""

    @API.doc('--caught/labels--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'CaughtLabels') -> Dict[str, Dict[str, Union[str, int]]]:
        """Caught moving object table labels."""
        data: Dict[str, Dict[str, Union[str, int]]] = COLUMN_LABELS['/']
        return data
