"""
ZTF Module
Creates RestPlus namespace for ZTF controller. Useful as a reference for
creating simple routes where a table row represents an entity.

"""

import logging
from typing import Dict, Any
import flask_restplus as FRP
from flask import request
from models.models import ztf_found_result
from services import query_ztf_data as qztf
from util import jsonify_output

API = FRP.Namespace(
    name="ZTF Fetching",
    path="/ztf",
    description="Zwicky Transient Facility survey metadata and ZChecker results."
)

logger: logging.Logger = logging.getLogger(__name__)

ztf_found_model: FRP.model.Model = API.model('ZTFFoundModel', {
    "start": FRP.fields.Integer,
    "end": FRP.fields.Integer,
    "maglimit": FRP.fields.Float,
    "objid": FRP.fields.Integer,
    "nightid": FRP.fields.Integer,
    "seeing": FRP.fields.Float,
    "data": FRP.fields.Nested(API.model('ZTFFoundResult', ztf_found_result)),
    "total": FRP.fields.Integer
})


@API.route("/found")
class ZTFFound(FRP.Resource):
    """Controller class for ZTF found database rows."""

    @API.doc('--ztf/found--')
    @API.param('maglimit', description='Optional. Require point source'
               ' sensitivity > this value.', _in='query')
    @API.param('nightid', description='Optional. Limit to this night.',
               _in='query')
    @API.param('objid', description='Optional. Search for this object id.',
               _in='query')
    @API.param('seeing', description='Optional. Require seeing (FWHM) <'
               ' this value (arcsec).', _in='query')
    @API.param('end', description='Optional. Paginated ending index.',
               _in='query')
    @API.param('start', description='Optional. Paginated starting index.',
               _in='query')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(ztf_found_model)
    def get(self: 'ZTFFound') -> Dict[str, Any]:
        """Query ZTF found objects."""

        # Extract params from URL
        maglimit: int = request.args.get('maglimit', 0, float)
        nightid: int = request.args.get('nightid', -1, int)
        objid: int = request.args.get('objid', -1, int)
        seeing: int = request.args.get('seeing', 0, float)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 50, int)

        # Pass params to data-provider-service
        found_ztf_data: list = qztf.query_ztf_found_data(
            start, end, maglimit=maglimit, nightid=nightid, objid=objid,
            seeing=seeing)

        return {
            "start": start,
            "end": end,
            "maglimit": maglimit,
            "objid": objid,
            "nightid": nightid,
            "seeing": seeing,
            "data": found_ztf_data,
            "total": len(found_ztf_data)
        }


@API.route("/found/objects")
class ZTFFoundObjects(FRP.Resource):
    """Controller class for ZTF found objects list."""

    @API.doc('--ztf/found/objects--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'ZTFFoundObjects') -> Dict[str, Any]:
        """ZTF found object list."""
        objects: list = qztf.query_ztf_found_objects()
        return {
            "data": objects,
            "total": len(objects)
        }


@API.route("/nights")
class ZTFNights(FRP.Resource):
    """Controller class for ZTF nights database."""

    @API.doc('--ztf/nights--')
    @API.param('nightid', description='Optional. Search for this night ID.',
               _in='query')
    @API.param('date', description='Optional. Search for this date.',
               _in='query')
    @API.param('end', description='Optional. Paginated ending index.',
               _in='query')
    @API.param('start', description='Optional. Paginated starting index.',
               _in='query')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'ZTFNights') -> Dict[str, Any]:
        """Query ZTF nights table."""

        # Extract params from URL
        nightid: int = request.args.get('nightid', 0, int)
        date: int = request.args.get('date', '', str)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 1000, int)

        # Pass params to data-provider-service
        ztf_nights_data: list = qztf.query_ztf_nights_data(
            start, end, nightid=nightid, date=date)

        # Package retrieved data as response json
        return {
            "start": start,
            "end": end,
            "nightid": nightid,
            "date": date,
            "data": ztf_nights_data,
            "total": len(ztf_nights_data)
        }
