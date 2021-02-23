"""App exceptions.

Classes intended to be caught by the API app are annotated with HTTP status
codes.

"""

from catch.exceptions import CatchException


class CatchApisException(Exception):
    """Generic CATCH APIs exception."""
