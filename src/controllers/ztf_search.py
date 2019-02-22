"""
ZTF Module
Creates RestPlus namespace for ZTF controller. Useful as a reference for
creating simple routes where a table row represents an entity.
"""

import logging
import flask_restplus as FRP
from flask import request, jsonify
from flask.wrappers import Response
from services import DATA_PROVIDER

API = FRP.Namespace(
    name='ZTF Namespace',
    path="/ztf",
    description='Demo route for treating rows within ZTF table as query-able entities'
)

logger: logging.Logger = logging.getLogger(__name__)


@API.route("/")
class ZTF(FRP.Resource):
    """Controller class for ZTF rows"""

    @API.doc('--ztf--')
    def get(self: 'ZTF') -> Response:
        """Returns ZTF row requests"""

        # Extract params from URL
        start: int = request.args.get('start', 0, int)
        end: int = request.args.get('end', 50, int)

        # Pass params to data-provider-service
        all_ztf_data = DATA_PROVIDER.query_all_ztf_data()

        # Package retrieved data as response json
        res: Response = jsonify(
            {
                "start": start,
                "end": end,
                "data": all_ztf_data,
                "total": len(all_ztf_data)
            }
        )
        res.status_code = 200
        return res