"""Object marshalling."""

from typing import Dict, List, Optional, Union
from astropy.time import Time
from catch.model import Found, Observation, SkyMapperDR4

SKYMAPPER_IMAGE_TYPES: Dict[str, str] = {
    "fs": "Shallow Survey",
    "ms": "Main Survey",
    "std": "Standard Field",
}

# attributes to serialize from all survey-specific data objects, keyed by field
# prefix (__field_prefix__ attribute on survey objects).
SURVEY_SPECIFIC_FIELDS: Dict[str, List[str]] = {
    "css": ["telescope"],
    "ps1": [
        "frame_id",
        "projection_id",
        "skycell_id",
    ],
    "skymapper": [
        "field_id",
        "image_type",
        "sb_mag",
        "zpapprox",
    ],
}


def skymapper_image_type(obs):
    if isinstance(obs, SkyMapperDR4):
        return SKYMAPPER_IMAGE_TYPES.get(obs.image_type)
    else:
        return None


def observation(
    obs: Observation,
    ra: Optional[float] = None,
    dec: Optional[float] = None,
) -> Dict[str, Union[str, float, int, None]]:
    """Transform observation object into a dictionary.

    Survey specific items are prefixed (see `SURVEY_SPECIFIC_FIELDS`).


    Parameters
    ----------
    obs : Observation
        The observation object from sqlalchemy.

    ra, dec : float, optional
        Coordinates for cutout and preview URLs, in units of degree.


    Returns
    -------
    data : dict

    """

    data: Dict[str, Union[str, float, int, None]] = {
        "observation_id": obs.observation_id,
        "product_id": obs.product_id,
        "source": obs.source,
        "source_name": obs.__data_source_name__,
        "mjd_start": obs.mjd_start,
        "mjd_stop": obs.mjd_stop,
        "fov": obs.fov,
        "filter": obs.filter,
        "exposure": obs.exposure,
        "seeing": obs.seeing,
        "airmass": obs.airmass,
        "maglimit": obs.maglimit,
        "date": Time((obs.mjd_start + obs.mjd_stop) / 2, format="mjd").iso,
        "archive_url": obs.archive_url,
        "diff_url": getattr(obs, "diff_url", None),
    }

    if ra is not None and dec is not None:
        data["cutout_url"] = obs.cutout_url(ra, dec)
        data["preview_url"] = obs.preview_url(ra, dec)

    # survey-specific fields
    prefix: str = getattr(obs, "__field_prefix__")
    for field in SURVEY_SPECIFIC_FIELDS.get(prefix, []):
        key = f"{prefix}:{field}"
        if key == "skymapper:image_type":
            value = skymapper_image_type(obs)
        else:
            value = getattr(obs, field)

        data[key] = value

    return data


def found(found: Found) -> Dict[str, Union[str, float, int, None]]:
    """Transform found object into a dictionary.


    Parameters
    ----------
    found : Found
        The found object from sqlalchmey.


    Returns
    -------
    data : dict

    """

    data: Dict[str, Union[str, float, int, None]] = {
        "found_id": found.found_id,
        "date": Time(found.mjd, format="mjd").iso,
        "rh": found.rh,
        "delta": found.delta,
        "phase": found.phase,
        "drh": found.drh,
        "true_anomaly": found.true_anomaly,
        "ra": found.ra,
        "dec": found.dec,
        "dra": found.dra,
        "ddec": found.ddec,
        "unc_a": found.unc_a,
        "unc_b": found.unc_b,
        "unc_theta": found.unc_theta,
        "elong": found.elong,
        "sangle": found.sangle,
        "vangle": found.vangle,
        "vmag": found.vmag,
    }

    return data
