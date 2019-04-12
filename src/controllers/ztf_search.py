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
    description="Zwicky Transient Facility survey metadata and ZChecker results."
)

logger: logging.Logger = logging.getLogger(__name__)


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
    def get(self: 'ZTFFound') -> Response:
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

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "start": start,
                "end": end,
                "maglimit": maglimit,
                "objid": objid,
                "nightid": nightid,
                "seeing": seeing,
                "data": found_ztf_data,
                "total": len(found_ztf_data)
            }
        )
        res.status_code = 200
        return res


@API.route("/found/metadata")
class ZTFFoundMetadata(FRP.Resource):
    """Controller class for ZTF found metadata."""

    @API.doc('--ztf/found/metadata--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'ZTFFoundMetadata') -> Response:
        """ZTF found object metadata."""
        ztf_found_metadata: list = qztf.query_ztf_found_metadata()

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "data": ztf_found_metadata,
                "total": len(ztf_found_metadata)
            }
        )
        res.status_code = 200
        return res


@API.route("/found/objects")
class ZTFFoundObjects(FRP.Resource):
    """Controller class for ZTF found objects list."""

    @API.doc('--ztf/found/objects--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'ZTFFoundObjects') -> Response:
        """ZTF found object list."""
        objects: list = qztf.query_ztf_found_objects()

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "data": objects,
                "total": len(objects)
            }
        )
        res.status_code = 200
        return res


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
    def get(self: 'ZTFNights') -> Response:
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


@API.route("/nights/metadata")
class ZTFNightsMetadata(FRP.Resource):
    """Controller class for ZTF nights metadata."""

    @API.doc('--ztf/nights/metdata--')
    @FRP.cors.crossdomain(origin='*')
    def get(self: 'ZTFNightsMetadata') -> Response:
        """ZTF nights metadata."""
        metadata: list = qztf.query_ztf_nights_metadata()

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "data": metadata,
                "total": len(metadata)
            }
        )
        res.status_code = 200
        return res
