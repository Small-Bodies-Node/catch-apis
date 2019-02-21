"""
This 'controllers' module defines the routes for the web application.
The organization of this module follows that of the 'apis' module in the
Flask-RESTPlus namespacing example: https://flask-restplus.readthedocs.io/en/stable/scaling.html
"""

import logging
import traceback
from typing import Any, Tuple
from flask_restplus import Api
from flask import jsonify
from flask.wrappers import Response
from sqlalchemy.orm.exc import NoResultFound

# Import all restplus namespaces
from .test_routes import API as ns2
from .moving_object_search import API as ns1

logger = logging.getLogger(__name__)
logger.warning('<><><> IMPORTING CONTROLLERS <><><>')

# Initiate RestPlusApi object:
REST_PLUS_APIS = Api(
    title='CATCH APIS',
    version='1.0',
    description='APIs for CATCH Tool',
    doc='/docs'
)

# Combine Namespaces
REST_PLUS_APIS.add_namespace(ns1)
REST_PLUS_APIS.add_namespace(ns2)

# Add error handlers:
@REST_PLUS_APIS.errorhandler
def default_error_handler(exception: Exception) -> Tuple[Response, Any]:
    """ -- Error Handler -- """
    message = 'An unhandled exception occurred. Error Message: ' + \
        str(exception)
    logger.exception(message)
    res: Response = jsonify({'message': message})
    return res, getattr(exception, 'code', 500)
    # return res, 500


@REST_PLUS_APIS.errorhandler(NoResultFound)
def database_not_found_error_handler(exception: Exception) -> Tuple[Response, int]:
    logger.warning(traceback.format_exc() +
                   " Error Message: \n\n" + str(exception))
    res: Response = jsonify(
        {'message': 'A database result was required but none was found. Exception message: \n\n'+str(exception)})
    return res, 404


logger.warning('Test Baby 2')
