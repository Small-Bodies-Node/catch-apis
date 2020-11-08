"""
This 'controllers' module defines the routes for the web application.
The organization of this module follows that of the 'apis' module in the
Flask-RESTPlus namespacing example: https://flask-restplus.readthedocs.io/en/stable/scaling.html
"""

# import os
import logging
import traceback
from typing import Any, Tuple
from flask_restplus import Api
from flask import jsonify, Blueprint
from flask.wrappers import Response
from sqlalchemy.orm.exc import NoResultFound
from env import ENV, EDeploymentTier as EDE

# Import all restplus namespaces
from .demo_routes import API as demos
from .query import API as query
from .images import API as images
from .stream import API as stream
from .caught import API as caught

logger: logging.Logger = logging.getLogger(__name__)
logger.info('"<><><> IMPORTING CONTROLLERS <><><>"')


# Choose base root to run app locally based on deployment tier
URL_PREFIX: str = '/api'
TITLE_SUFFIX: str = f'[{ENV.DEPLOYMENT_TIER.name}]'

# Define flask blueprint to apply prefix to whole api
blueprint: Blueprint = Blueprint(
    'some_blueprint_name',
    __name__,
    url_prefix=URL_PREFIX
)


descriptionHtml = """
<p>
  This is a swagger interface to the APIs for SBN\'s CATCH Tool.
</p>

<p>
  The frontend can be found <a href="https://catch.astro.umd.edu">here</a>.
  See the <a href="https://catch.astro.umd.edu/apis">Apis</a> section for descriptions on how to use these api routes.
</p>

<p>
  This interface is generated automatically by the <a href="https://flask-restplus.readthedocs.io/en/stable/">flask_restplus library</a>.
</p>
"""

# Initiate RestPlusApi object and associate it with blueprint
REST_PLUS_APIS = Api(
    blueprint,
    # title='CATCH APIS '+str(TITLE_SUFFIX),
    title='CATCH SWAGGER UI '+str(TITLE_SUFFIX),
    version='1.0',
    description=descriptionHtml,
    doc='/docs'
)

# Combine Namespaces
REST_PLUS_APIS.add_namespace(query)
REST_PLUS_APIS.add_namespace(caught)
REST_PLUS_APIS.add_namespace(images)
REST_PLUS_APIS.add_namespace(stream)
REST_PLUS_APIS.add_namespace(demos)

# Add error handlers


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
