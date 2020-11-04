"""Image services."""

from typing import Any, Union
from env import ENV
from catch import Catch


def build_cutout_url(row: Any, size: int = 1, prefix: str = '') -> str:
    """Build the URL for cutout images.

    Parameters
    ----------
    row : sqlalchemy result
        Found, Obs, Obj

    size : int, optional
        Size of the cutout (square) in arcmin.

    prefix : string, optional
        File prefix for locally produced cutouts.

    """

    r: float = row.Found.ra % 360
    d: float = min(max(row.Found.dec, -90), 90)
    s: float = max(1, size)

    url: str
    if row.Obs.source[:4] == "neat":
        url = '{}/{}{}_ra{:09.5f}_dec{:+09.5f}_{:d}arcmin.fits'.format(
            ENV.CATCH_CUTOUT_BASE_URL, prefix, row.Obs.productid, r, d, s)
    elif row.Obs.source == "skymapper":
        url = Catch.skymapper_cutout_url(row.Found, row.Obs, size=s / 60)

    return url


def build_fullframe_url(row: Any) -> Union[str, None]:
    """Build the URL for full-frame images.

    Parameters
    ----------
    row : sqlalchemy result
        Found, Obs, Obj

    """

    url: str
    if row.Obs.source[:4] == "neat":
        path: str
        if row.Obs.source[5:] == "palomar":
            path = 'tricam'
        else:
            # Maui GEODSS
            path = 'geodss'

        url = '{}/neat/{}/data/{}.fits'.format(
            ENV.CATCH_ARCHIVE_BASE_URL, path,
            '/'.join(row.Obs.productid.lower().split('_')))
    else:
        # full-frame only for NEAT
        return None

    return url
