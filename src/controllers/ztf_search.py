"""
ZTF Module
Creates RestPlus namespace for ZTF controller. Useful as a reference for
creating simple routes where a table row represents an entity.

"""

import logging
from typing import Dict, List, Any
import flask_restplus as FRP
from flask import request
from models.ztf import App
from services import query_ztf_data
from util import jsonify_output

API: FRP.Namespace = App.api

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/found")
class ZTFFound(FRP.Resource):
    """Controller class for ZTF found database rows."""

    @API.doc('--ztf/found--')
    @API.param(
        'maglimit', _in='query',
        description='Optional. Require point source sensitivity > this value.'
    )
    @API.param(
        'nightid', _in='query',
        description='Optional. Limit to this night.'
    )
    @API.param(
        'objid', _in='query',
        description='Optional. Search for this object id.'
    )
    @API.param(
        'seeing', _in='query',
        description='Optional. Require seeing (FWHM) < this value (arcsec).'
    )
    @API.param(
        'end', _in='query',
        description='Optional. Paginated ending index.'
    )
    @API.param(
        'start', _in='query',
        description='Optional. Paginated starting index.'
    )
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(App.found)
    def get(self: 'ZTFFound') -> Dict[str, object]:
        """Query ZTF found objects."""

        # Extract params from URL
        maglimit: float = request.args.get('maglimit', 0, float)
        nightid: int = request.args.get('nightid', -1, int)
        objid: int = request.args.get('objid', -1, int)
        seeing: float = request.args.get('seeing', 0, float)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 50, int)

        # Pass params to data-provider-service
        data: List[dict] = query_ztf_data.found(
            start, end, maglimit=maglimit, nightid=nightid, objid=objid,
            seeing=seeing)

        return {
            'data': data,
            'maglimit': maglimit,
            'nightid': nightid,
            'objid': objid,
            'seeing': seeing,
            'start': start,
            'end': end,
            'total': len(data)
        }


@API.route("/found/<int:foundid>")
class ZTFFoundID(FRP.Resource):
    """Controller class for ZTF found table search by foundid."""

    @API.doc('--ztf/found/foundid--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(App.found_data)
    def get(self: 'ZTFFound', foundid: int) -> dict:
        """Query ZTF found objects by found ID."""

        data: List[dict] = query_ztf_data.found(foundid=foundid)

        return data[0]


@API.route("/found/objects")
class ZTFFoundObjects(FRP.Resource):
    """Controller class for ZTF found objects list."""

    @API.doc('--ztf/found/objects--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    @API.marshal_with(App.found_objects)
    def get(self: 'ZTFFoundObjects') -> Dict[str, Any]:
        """ZTF found object list."""
        data: List[dict] = query_ztf_data.found_objects()
        return {
            "data": data,
            "total": len(data)
        }


@API.route("/found/labels")
class ZTFFoundLabels(FRP.Resource):
    """Controller for ZTF found object column labels."""

    @API.doc('--ztf/found/labels--')
    @FRP.cors.crossdomain(origin='*')
    @jsonify_output
    def get(self: 'ZTFFoundLabels') -> Dict[str, Dict[str, str]]:
        """ZTF found object table labels."""
        data: Dict[str, Dict[str, str]] = (
            query_ztf_data.column_labels('/found'))
        return data


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
    @API.marshal_with(App.nights)
    def get(self: 'ZTFNights') -> Dict[str, Any]:
        """Query ZTF nights table."""

        # Extract params from URL
        nightid: int = request.args.get('nightid', 0, int)
        date: str = request.args.get('date', '', str)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 1000, int)

        # Pass params to data-provider-service
        data: List[dict] = query_ztf_data.nights(
            start, end, nightid=nightid, date=date)

        # Package retrieved data as response json
        return {
            "start": start,
            "end": end,
            "nightid": nightid,
            "date": date,
            "data": data,
            "total": len(data)
        }
