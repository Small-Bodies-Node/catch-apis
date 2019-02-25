"""
Moving-Object-Search (MOS) Module
Creates RestPlus namespace for MOS controllers.
"""

import typing
import logging
from flask import request
from flask_restplus import Namespace, Resource, fields
from werkzeug.exceptions import BadRequest
from services import DATA_PROVIDER

API = Namespace(
    name='Moving Object Search (MOS)',
    path="/moving-object-search",
    description="Controls request-response cycle for MOS;\
        essentially a join between ZTF and Found tables filtered on an objid."
)

MOS_RETURN_MODEL: Namespace.model = API.model('MOS-RETURN-MODEL', {
    'data': fields.Raw(required=False, description='Data rows of join between ZTF and Found tables'),
    'total': fields.Integer(required=False, description='Total number of rows of data'),
    'objid': fields.String(required=True, description='The objid of the MOS object'),
    'start': fields.Integer(required=False, description='Starting row for paginated return'),
    'end': fields.Integer(required=False, description='End row for paginated return'),
})

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/")
class MovingObjectSearch(Resource):
    """Controller class for moving-object-search"""

    @API.param('end', description='Optional. Paginated ending index', _in='query')
    @API.param('start', description='Optional. Paginated starting index', _in='query')
    @API.param('objid', description='Required. Objid of the moving-search-object', _in='query')
    @API.marshal_with(MOS_RETURN_MODEL, envelope='resource')
    def get(self: 'MovingObjectSearch') -> typing.Tuple[typing.Dict, int]:
        """Returns moving-object-search requests"""

        # Extract params from URL and ensure there's an objid
        objid: str = request.args.get('objid', 'Objid of MOS', str)
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 50, int)
        if not isinstance(objid, str):
            raise BadRequest('An objid must be provided!!!')

        # Pass params to data-provider-service
        mos_data = DATA_PROVIDER.query_moving_object_search(
            objid, start, end)

        # Package retrieved data as a dictionary
        res: MOS_RETURN_MODEL = {
            "objid": objid,
            "start": start,
            "end": end,
            "data": mos_data,
            "total": len(mos_data)
        }

        return res, 200
