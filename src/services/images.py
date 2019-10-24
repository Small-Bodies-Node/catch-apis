"""Image services."""

from typing import Optional
from env import ENV


def build_url(productid: str, ra: Optional[float] = None,
              dec: Optional[float] = None, size: int = 1) -> str:
    """Build the URL for full-frame and cutout images."""

    url: str
    if None in [ra, dec]:
        # full frame URL
        path: str
        if productid[0] == 'G':
            path = 'geodss'
        else:
            path = 'tricam'

        url = '{}/neat/{}/data/{}.fits'.format(
            ENV.CATCH_FULLFRAME_BASE_URL, path,
            '/'.join(productid.lower().split('_')))
    else:
        r: float = ra % 360
        d: float = min(max(dec, -90), 90)
        s: float = max(1, size)

        # cutout URL
        url = '{}/{}_ra{:09.5f}_dec{:+09.5f}_{:d}arcmin.fits'.format(
            ENV.CATCH_CUTOUT_BASE_URL, productid, ra, dec, size)

    return url
