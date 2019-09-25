"""
This 'controllers' module defines the routes for the web application.
The organization of this module follows that of the 'apis' module in the
Flask-RESTPlus namespacing example: https://flask-restplus.readthedocs.io/en/stable/scaling.html
"""

# import os
import logging
import traceback
from typing import Any, Tuple, Optional
from flask_restplus import Api
from flask import jsonify, Blueprint
from flask.wrappers import Response
from sqlalchemy.orm.exc import NoResultFound
from env import ENV, EDeploymentEnvironment as EDE

# Import all restplus namespaces
from .demo_routes import API as ns0
from .neat import API as ns1

logger: logging.Logger = logging.getLogger(__name__)
logger.info('"<><><> IMPORTING CONTROLLERS <><><>"')


# Choose port to run app locally based on deployment environment
if ENV.DEPLOYMENT_ENV == EDE.PROD:
    URL_PREFIX = '/catch'
    title_suffix = ''
elif ENV.DEPLOYMENT_ENV == EDE.STAGE:
    URL_PREFIX = '/catch-stage'
    title_suffix = '[STAGE]'
elif ENV.DEPLOYMENT_ENV == EDE.DEV:
    URL_PREFIX = '/catch-dev'
    title_suffix = '[DEV]'
else:
    raise Exception('Unrecognized DEPLOYMENT_ENV!')


# Define flask blueprint to apply prefix to whole api
blueprint: Blueprint = Blueprint(
    'some_blueprint_name',
    __name__,
    url_prefix=URL_PREFIX)

# Initiate RestPlusApi object and associate it with blueprint
REST_PLUS_APIS = Api(
    blueprint,
    title='CATCH APIS '+str(title_suffix),
    version='1.0',
    description='Flask APIs for CATCH Tool',
    doc='/docs'
)

# Combine Namespaces
REST_PLUS_APIS.add_namespace(ns0)
REST_PLUS_APIS.add_namespace(ns1)

# Add error handlers:
@REST_PLUS_APIS.errorhandler
def default_error_handler(exception: Exception) -> Tuple[Response, Any]:
    """ -- Default Error Handler -- """
    message = 'An unhandled exception occurred. Error Message: ' + \
        str(exception)
    logger.exception(message)
    res: Response = jsonify({'message': message})
    return res, getattr(exception, 'code', 500)
    # return res, 500


@REST_PLUS_APIS.errorhandler(NoResultFound)
def database_not_found_error_handler(exception: Exception) -> Response:
    """ -- DB Error Handler -- """
    error_message: str = traceback.format_exc() + " Error Message: \n\n" + \
        str(exception)
    logger.warning(error_message)
    res: Response = jsonify(
        {
            "message":
            """
                A database result was required but none was found.
                Exception message: \n\n
            """ + str(exception)
        }
    )
    res.status_code = 404
    return res
