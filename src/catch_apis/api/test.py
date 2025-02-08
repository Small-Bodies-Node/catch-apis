"""API route just for testing environments."""

import os
from flask import send_file, Response
from .. import services


def data(filename: str, ra: float | None = None, dec: float | None = None) -> Response:
    if filename.endswith("xml"):
        mime_type = "text/plain"
        content = services.test.label(filename)
    else:
        if filename.endswith(("fit", "fits")):
            mime_type = "image/fits"
            content = services.test.fits(ra, dec)
        elif filename.endswith(("jpeg", "jpg")):
            mime_type = "image/jpeg"
            content = services.test.jpeg(ra, dec)

        if None not in (ra, dec):
            root, ext = os.path.splitext(filename)
            filename = f"{root}_ra{ra}_dec{dec}{ext}"

    # content should be a file pointer (do not use file names from the route)
    return send_file(
        content,
        mimetype=mime_type,
        as_attachment=filename.endswith(("fit", "fits")),
        download_name=filename,
    )
