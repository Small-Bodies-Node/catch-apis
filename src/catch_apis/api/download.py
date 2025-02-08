from .. import services
from .. import __version__ as version


def package(body: dict) -> str:
    """Controller for packaging data."""
    return services.download.package(body["images"])
