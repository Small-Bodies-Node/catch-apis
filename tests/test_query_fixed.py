"""
A few simple tests to see that the API is working.

To see messages returned from the API, e.g., to debug failing tests:

    pytest --capture=tee-sys

These tests are currently hard-coded for DEPLOYMENT_TIER=LOCAL in .env.

"""

import requests

def test_point():
    # Crab nebula
    parameters = {
        "ra": "05:34:32.0",
        "dec": "+22 00 48",
    }
    response = requests.get(f"http://127.0.0.1:5000/fixed/point", parameters)
    response.raise_for_status()
    results = response.json()
    assert results["message"] == ""
    assert results["query"]["ra"] == parameters["ra"]
    assert results["query"]["dec"] == parameters["dec"]
    assert "neat_palomar_tricam" in results["query"]["sources"]
    assert len(results["data"]) == 428  # no independently verified
    product_ids = [obs["product_id"] for obs in results["data"]]

    # these are verified to be the Crab:
    assert "rings.v3.skycell.1784.059.wrp.g.55560_46188.fits" in product_ids
    assert "urn:nasa:pds:gbo.ast.catalina.survey:data_calibrated:703_20211108_2b_n24018_01_0002.arch" in product_ids