"""Data generators for testing environments."""

import io
import numpy as np
from astropy.io import fits as pyfits
from PIL import Image


def _image(ra, dec):
    im = np.zeros((100, 100))
    if None not in (ra, dec):
        im[:10, :] = ra
        im[:, :10] = dec
    return im


def label(filename):
    content = f"""<?xml version="1.0"?>
<filename>{filename}</filename>
"""
    return io.BytesIO(content.encode())


def fits(ra, dec):
    hdul = pyfits.HDUList()
    hdul.append(pyfits.PrimaryHDU(_image(ra, dec)))

    fp = io.BytesIO()
    hdul.writeto(fp)
    fp.seek(0)

    return fp


def jpeg(ra, dec):
    im = _image(ra, dec)[::-1]
    im = (im - im.min()) / np.ptp(im) * 255
    im = Image.fromarray(im.astype(np.uint8)).convert("L")

    fp = io.BytesIO()
    im.save(fp, format="jpeg")
    fp.seek(0)

    return fp
