"""
Moving-Object-Search (MOS) Module
Creates RestPlus namespace for MOS controllers.
"""

from typing import Any
from flask import request, jsonify
from flask.wrappers import Response
from flask_restplus import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest
# from controllers import logger
import logging
from services import DATA_PROVIDER

API = Namespace('moving-object-search',
                description='Controls Request-Response Cycle For M-O-S')

MOS = API.model('MOS-RETURN', {
    'data': fields.Arbitrary(required=True, description='Data rows'),
    'total': fields.Integer(required=False, description='Total number of rows of data'),
    'objid': fields.String(required=True, description='The objid of the ZTF object'),
    'start': fields.Integer(required=False, description='Starting row for paginated return'),
    'end': fields.Integer(required=False, description='End row for paginated return'),
})

logger = logging.getLogger(__name__)
logger.info("<><><> IMPORTING MOS <><><>")


@API.route("")
class MovingObjectSearch(Resource):
    """Controller class for moving-object-search"""

    @API.doc('--mos--')
    def get(self: Any) -> Response:
        """Returns moving-object-search requests"""

        # Extract params from URL
        objid: str = request.args.get('objid', 'xxxxx', str)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 50, int)

        if not isinstance(objid, str):
            print("denied~!~")
            raise BadRequest('My custom message')

        # logger.critical("Test Logging")

        # Pass params to data-provider-service
        mos_data = DATA_PROVIDER.query_moving_object_search(
            objid, start, end)

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "objid": objid,
                "start": start,
                "end": end,
                "data": mos_data,
                "total": len(mos_data)
            }
        )
        return res
