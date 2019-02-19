"""
This 'controllers' module defines the routes for the web application.
The organization of this module follows that of the 'apis' module in the
Flask-RESTPlus namespacing example: https://flask-restplus.readthedocs.io/en/stable/scaling.html
"""

from flask_restplus import Api

# Import all restplus namespaces
from .moving_object_search import API as ns1

# Initiate RestPlusApi object:
rest_plus_apis = Api(
    title='CATCH APIS',
    version='1.0',
    description='APIs for CATCH Tool',
    doc='/docs/'
)

# Combine Namespaces
rest_plus_apis.add_namespace(ns1)
# rest_plus_apis.add_namespace(ns2)
