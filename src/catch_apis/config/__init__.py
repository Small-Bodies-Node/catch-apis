from typing import List
import enum

from .logging import get_logger  # noqa: F401
from .exceptions import CatchApisException, CatchException  # noqa: F401


# users are allowed to search these sources through the API
allowed_sources: List[str] = [
    "atlas_haleakela",
    "atlas_mauna_loa",
    "atlas_rio_hurtado",
    "atlas_sutherland",
    "catalina_bigelow",
    "catalina_lemmon",
    "catalina_bokneosurvey",
    "loneos",
    "neat_palomar_tricam",
    "neat_maui_geodss",
    "ps1dr2",
    "skymapper_dr4",
    "spacewatch",
]


class QueryStatus(enum.Enum):
    UNDEFINED: str = "undefined"
    SUCCESS: str = "success"
    QUEUED: str = "queued"
    QUEUEFULL: str = "queue full"
    FAILED: str = "failed"
