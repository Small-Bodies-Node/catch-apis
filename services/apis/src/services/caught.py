import uuid
from typing import Any, Dict, List, Union

from astropy.time import Time
from catch.model import Found, Observation, SkyMapper, PS1DR2

from .catch_manager import Catch, catch_manager


SKYMAPPER_IMAGE_TYPES: Dict[str, str] = {
    'fs': 'Shallow Survey',
    'ms': 'Main Survey',
    'std': 'Standard Field'
}

# attributes to serialize from all survey-specific data objects, keyed by field
# prefix (__field_prefix__ attribute on survey objects).
SURVEY_SPECIFIC_FIELDS: Dict[str, List[str]] = {
    'css': ['telescope'],
    'ps1': [
        "frame_id",
        "projection_id",
        "skycell_id",
    ],
    'skymapper': [
        'field_id',
        'image_type',
        'sb_mag',
        'zpapprox',
    ]
}


def caught(job_id: uuid.UUID) -> List[Dict[str, Any]]:
    """Caught object results.


    Parameters
    ----------
    job_id : uuid.UUID
        Unique job id for the search.


    Return
    ------
    caught_observations : list of dict

    """

    # unpack into list of dictionaries for serialization
    caught_observations: List[Dict[str, Any]]
    caught_observations = []

    catch: Catch
    with catch_manager() as catch:
        data: List[Any] = catch.caught(job_id)

        found: Found
        obs: Observation
        for (found, obs) in data:
            caught_obs: Dict[str, Union[str, float, int, None]] = {
                'product_id': obs.product_id,
                'source': obs.source,
                'source_name': obs.__data_source_name__,
                'mjd_start': obs.mjd_start,
                'mjd_stop': obs.mjd_stop,
                "filter": obs.filter,
                "exposure": obs.exposure,
                "seeing": obs.seeing,
                "airmass": obs.airmass,
                "maglimit": obs.maglimit,
                'date': Time(found.mjd, format='mjd').iso,
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
                "archive_url": obs.archive_url,
                "cutout_url": obs.cutout_url(found.ra, found.dec),
                "preview_url": obs.preview_url(found.ra, found.dec),
            }

            # survey-specific fields
            prefix: str = getattr(obs, '__field_prefix__')
            for field in SURVEY_SPECIFIC_FIELDS.get(prefix, []):
                key = f"{prefix}:{field}"
                if key == 'skymapper:image_type':
                    value = skymapper_image_type(obs)
                else:
                    value = getattr(obs, field)

                caught_obs[key] = value

            caught_observations.append(caught_obs)

    return caught_observations


def skymapper_image_type(obs):
    if isinstance(obs, SkyMapper):
        return SKYMAPPER_IMAGE_TYPES.get(obs.image_type)
    else:
        return None
