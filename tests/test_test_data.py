"""Test the test/data route."""

import io
from PIL import Image
import numpy as np
from astropy.io import fits
from starlette.testclient import TestClient
from . import fixture_test_client


def test_label(test_client: TestClient):
    response = test_client.get("/test/data/image.xml")
    response.raise_for_status()

    assert "image.xml" in response.content.decode()


def test_fits(test_client: TestClient):
    response = test_client.get("/test/data/image.fits")
    response.raise_for_status()

    fp = io.BytesIO(response.content)
    with fits.open(fp) as hdul:
        assert np.all(hdul[0].data == 0)

    parameters = {
        "ra": "10",
        "dec": "-20",
    }

    response = test_client.get("/test/data/image.fits", params=parameters)
    response.raise_for_status()

    fp = io.BytesIO(response.content)
    with fits.open(fp) as hdul:
        im = hdul[0].data
        assert im[0, 50] == 10
        assert im[50, 0] == -20


def test_jpeg(test_client: TestClient):
    parameters = {
        "ra": "10",
        "dec": "-20",
    }

    response = test_client.get("/test/data/image.jpeg", params=parameters)
    response.raise_for_status()

    fp = io.BytesIO(response.content)
    Image.open(fp, formats=["jpeg"])
