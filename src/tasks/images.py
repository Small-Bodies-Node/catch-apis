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
from tasks.logger import logger


def neat_cutout(productid: str, job_id: uuid.UUID, ra: float,
                dec: float, size: int = 5, prefix: str = '',
                overwrite: bool = False, thumbnail: bool = True,
                preview: bool = True) -> bool:
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

    preview : bool, optional
        Generate JPEG preview (full size) image.


    Returns
    -------
    success : bool
        ``True`` if a cutout was generated.

    """

    ra = ra % 360
    dec = min(max(dec, -90), 90)
    size = max(1, size)

    path: List[str] = [
        ENV.CATCH_ARCHIVE_PATH, 'neat',
        'geodss' if productid[0] == 'G' else 'tricam',
        'data'] + productid.lower().split('_')
    inf: str = '{}.fit.fz'.format(os.path.join(*path))

    basename: str = ('{}/{}{}_ra{:09.5f}_dec{:+09.5f}_{}arcmin'
                     .format(ENV.CATCH_CUTOUT_PATH, prefix, productid,
                             ra, dec, size))
    outf: str = '{}.fits'.format(basename)
    thumbf: str = '{}_thumb.jpg'.format(
        basename.replace(ENV.CATCH_CUTOUT_PATH, ENV.CATCH_THUMBNAIL_PATH))
    previewf: str = '{}.jpg'.format(
        basename.replace(ENV.CATCH_CUTOUT_PATH, ENV.CATCH_THUMBNAIL_PATH))

    logger.info('Cutout for {}: {}'.format(
        job_id.hex, ' → '.join((inf, outf))))

    if not os.path.exists(inf):
        logger.error('  Source file missing.')
        return False

    fn: str
    if (not overwrite) and all([os.path.exists(fn) for fn in (outf, thumbf, previewf)]):
        logger.debug('  All cutouts already exist.')
        return False

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
        return False

    cutout: CCDData = ccd[i]
    if (not os.path.exists(outf)) or overwrite:
        cutout.write(outf, overwrite=True)
        logger.debug('  Wrote {0} ({1[0]}×{1[1]} image)'.format(
            outf, cutout.shape))

    if thumbnail or preview:
        zscale: ZScaleInterval = ZScaleInterval()
        vmin: float
        vmax: float
        vmin, vmax = zscale.get_limits(cutout.data)

    if thumbnail and ((not os.path.exists(thumbf)) or overwrite):
        array_to_thumbnail(cutout.data, vmin, vmax, thumbf)
        logger.debug('  Wrote {}'.format(thumbf))

    if preview and ((not os.path.exists(previewf)) or overwrite):
        array_to_preview(cutout.data, vmin, vmax, previewf)
        logger.debug('  Wrote {}'.format(previewf))

    return True


def array_to_thumbnail(data: np.ndarray, vmin: float, vmax: float,
                       filename: str) -> None:
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
    im.save(filename, "JPEG", quality="web_low")


def array_to_preview(data: np.ndarray, vmin: float, vmax: float,
                     filename: str) -> None:
    """Convert array to JPEG preview (full size) image.


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
    im.save(filename, "JPEG", quality="web_low")
