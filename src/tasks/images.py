"""Tasks for CATCH searches."""

import os
import uuid
import logging
from typing import List, Tuple

from PIL import Image
import numpy as np
import astropy.units as u
from astropy.coordinates import Angle
from astropy.wcs import WCS
from astropy.nddata import CCDData
from astropy.io import fits
from astropy.visualization import ZScaleInterval

from env import ENV

logger: logging.Logger = logging.getLogger(__name__)


def neat_cutout(productid: str, job_id: uuid.UUID, ra: float,
                dec: float, size: int = 5, prefix: str = '',
                overwrite: bool = False, thumbnail: bool = True) -> None:
    """Cutout NEAT image at location.

    Parameters
    ----------
    productid : string
        NEAT PDS archive product ID.

    job_id : uuid.UUID
        Unique job ID.

    ra, dec : float
        Cutout center Right Acension and Declination, degrees.

    size : int, optional
        Cutout size, arcminutes.

    prefix : str, optional
        File name prefix.

    overwrite : bool, optional
        Overwrite existing files.

    thumbnail : bool, optional
        Generate JPEG thumbnail.

    """

    ra = ra % 360
    dec = min(max(dec, -90), 90)
    size = max(1, size)

    path: List[str] = [
        ENV.CATCH_ARCHIVE_PATH, 'neat',
        'geodss' if productid[0] == 'G' else 'tricam',
        'data'] + productid.lower().split('_')
    inf: str = '{}.fit.fz'.format(os.path.join(*path))

    outf: str = ('{}/{}{}_ra{:09.5f}_dec{:+09.5f}_{}arcmin.fits'
                 .format(ENV.CATCH_CUTOUT_PATH, prefix, productid,
                         ra, dec, size))

    logger.info('Cutout for {}: {}'.format(
        job_id.hex, ' → '.join((inf, outf))))

    if os.path.exists(outf) and not overwrite:
        logger.debug('  Already exists.')
        return

    # read data
    im: np.ndarray
    h: fits.Header
    im, h = fits.getdata(inf, header=True)

    # header is crashing WCS, so generate one "manually"
    wcs = WCS(naxis=2)
    wcs.wcs.ctype = h['CTYPE1'], h['CTYPE2']
    wcs.wcs.crval = h['CRVAL1'], h['CRVAL2']
    wcs.wcs.crpix = h['CRPIX1'], h['CRPIX2']
    wcs.wcs.cdelt = h['CDELT1'], h['CDELT2']
    k: str
    for k in ['CTYPE1', 'CTYPE2', 'CRVAL1', 'CRVAL2',
              'CRPIX1', 'CRPIX2', 'CDELT1', 'CDELT2']:
        del h[k]
    ccd: CCDData = CCDData(im, meta=h, wcs=wcs, unit='adu')

    s: u.Quantity = u.Quantity(size * u.arcmin)
    r: Angle = Angle(ra, 'deg')
    d: Angle = Angle(dec, 'deg')
    x0: float
    y0: float
    x0, y0 = wcs.all_world2pix([[ra, dec]], 0)[0]

    corners: np.ndarray = Angle([
        [r - s, d - s],
        [r + s, d - s],
        [r + s, d + s],
        [r - s, d + s]
    ]).deg

    x: np.ndarray
    y: np.ndarray
    x, y = wcs.all_world2pix(corners, 0).T.astype(int)

    i: Tuple[slice, slice] = np.s_[
        max(0, y.min()):min(y.max(), im.shape[0]),
        max(0, x.min()):min(x.max(), im.shape[1])
    ]
    if i[0].start == i[0].stop or i[1].start == i[1].stop:
        logger.error('Cutout has a length = 0 dimension.')
        return

    cutout: CCDData = ccd[i]
    cutout.write(outf, overwrite=True)
    logger.debug('  Wrote {}×{} image'.format(*cutout.shape))

    if thumbnail:
        zscale: ZScaleInterval = ZScaleInterval()
        vmin: float
        vmax: float
        vmin, vmax = zscale.get_limits(cutout.data)
        thumbf: str = (
            outf.replace(ENV.CATCH_CUTOUT_PATH, ENV.CATCH_THUMBNAIL_PATH)
            .replace('.fits', '_thumb.jpg'))
        array_to_thumbnail(cutout.data, vmin, vmax, thumbf)


def array_to_thumbnail(data: np.ndarray, vmin: float, vmax: float,
                       filename: str):
    """Convert array to JPEG thumbnail and save.


    Parameters
    ----------
    data : numpy.ndarray
        Data.

    vmin, vmax : float
        Color scale data minimum and maximum.

    filename : str
        File name.

    """

    # reverse y-axis for standard astronomical orientation
    scaled: np.ndarray = ((data[::-1] - vmin) / (vmax - vmin)) * 255
    scaled = np.minimum(np.maximum(0, scaled), 255)
    im: Image = Image.fromarray(np.uint8(scaled), 'L')
    im.thumbnail((128, 128))
    im.save(filename, "JPEG")
    logger.debug('  Wrote thumbnail'.format(filename))
