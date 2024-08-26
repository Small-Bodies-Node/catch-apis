from typing import List
import enum

from .logging import get_logger  # noqa: F401
from .exceptions import CatchApisException, CatchException


# users are allowed to search these sources through the API
allowed_sources: List[str] = [
    "neat_palomar_tricam",
    "neat_maui_geodss",
    "skymapper_dr4",
    "ps1dr2",
    "catalina_bigelow",
    "catalina_lemmon",
    "catalina_bokneosurvey",
    "spacewatch",
    "loneos",
]


class QueryStatus(enum.Enum):
    UNDEFINED: str = "undefined"
    SUCCESS: str = "success"
    QUEUED: str = "queued"
    QUEUEFULL: str = "queue full"
    FAILED: str = "failed"
