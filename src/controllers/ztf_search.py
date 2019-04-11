"""
ZTF Module
Creates RestPlus namespace for ZTF controller. Useful as a reference for
creating simple routes where a table row represents an entity.
This example does not use restplus models for response marshalling
"""

import logging
import flask_restplus as FRP
from flask import request, jsonify
from flask.wrappers import Response
from services import query_ztf_data as qztf


API = FRP.Namespace(
    name="ZTF Fetching",
    path="/ztf",
    description="ZTF survey metadata and ZChecker results."
)

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/found")
class ZTFFound(FRP.Resource):
    """Controller class for ZTF found database rows."""

    @API.doc('--ztf/found--')
    @API.param('objid', description='Optional. Search for this object id.', _in='query')
    @API.param('end', description='Optional. Paginated ending index.', _in='query')
    @API.param('start', description='Optional. Paginated starting index.', _in='query')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'ZTF') -> Response:
        """Returns ZTF found database row requests."""

        # Extract params from URL
        objid: int = request.args.get('objid', 0, int)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 50, int)

        # Pass params to data-provider-service
        found_ztf_data: list = qztf.query_ztf_found_data(
            start, end, objid=objid)

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "start": start,
                "end": end,
                "objid": objid,
                "data": found_ztf_data,
                "total": len(found_ztf_data)
            }
        )
        res.status_code = 200
        return res


@API.route("/nights")
class ZTFNights(FRP.Resource):
    """Controller class for ZTF nights database."""

    @API.doc('--ztf/nights--')
    @API.param('nightid', description='Optional. Search for this night ID.', _in='query')
    @API.param('date', description='Optional. Search for this date.', _in='query')
    @API.param('end', description='Optional. Paginated ending index.', _in='query')
    @API.param('start', description='Optional. Paginated starting index.', _in='query')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'ZTF') -> Response:
        """Returns ZTF found database row requests"""

        # Extract params from URL
        nightid: int = request.args.get('nightid', 0, int)
        date: int = request.args.get('date', '', str)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 1000, int)

        # Pass params to data-provider-service
        ztf_nights_data: list = qztf.query_ztf_nights_data(
            start, end, nightid=nightid, date=date)

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "start": start,
                "end": end,
                "nightid": nightid,
                "date": date,
                "data": ztf_nights_data,
                "total": len(ztf_nights_data)
            }
        )
        res.status_code = 200
        return res
