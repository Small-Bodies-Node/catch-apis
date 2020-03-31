"""/caught namspace and data models."""

from typing import Dict, Union
from flask_restplus import Namespace, Model, fields


class App:
    """/caught route namespace and return data models."""
    api: Namespace = Namespace(
        'Caught moving targets',
        path="/caught"
    )

    caught_data: Model = api.model('CaughtData', {
        "designation": fields.String(
            attribute='Obj.desg',
            description='Object designation'
        ),
        "jd": fields.Float(
            attribute='Found.jd',
            description='mid-point of the observation and epoch for'
            ' ephemeris (Julian date)'
        ),
        "ra": fields.Float(
            attribute='Found.ra',
            description='ephemeris Right Ascension (deg)'
        ),
        "dec": fields.Float(
            attribute='Found.dec',
            description='ephemeris Declination (deg)'
        ),
        "dra": fields.Float(
            attribute='Found.dra',
            description='RA * cos(Dec) rate of change (arcsec/hr)'
        ),
        "ddec": fields.Float(
            attribute='Found.ddec',
            description='Declination rate of change (arcsec/hr)'
        ),
        "unc_a": fields.Float(
            attribute='Found.unc_a',
            description='Error ellipse semi-major axis (arcsec)'
        ),
        "unc_b": fields.Float(
            attribute='Found.unc_b',
            description='Error ellipse semi-minor axis (arcsec)'
        ),
        "unc_theta": fields.Float(
            attribute='Found.unc_theta',
            description='Error ellipse position angle (deg)'
        ),
        "vmag": fields.Float(
            attribute='Found.vmag',
            description='brightness estimate (magnitude); for comet ephemerides from JPL, this value is T-mag, if available, otherwise N-mag'
        ),
        "rh": fields.Float(
            attribute='Found.rh',
            description='heliocentric distance (au)'
        ),
        "rdot": fields.Float(
            attribute='Found.rdot',
            description='heliocentric distance rate of change (km/s)'
        ),
        "delta": fields.Float(
            attribute='Found.delta',
            description='observer-target distance (au)'
        ),
        "phase": fields.Float(
            attribute='Found.phase',
            description='phase angle (degrees)'
        ),
        "selong": fields.Float(
            attribute='Found.selong',
            description='solar elongation (degrees)'
        ),
        "sangle": fields.Float(
            attribute='Found.sangle',
            description='projected comet-sun vector position angle'
            ' (degrees E of N)'
        ),
        "vangle": fields.Float(
            attribute='Found.vangle',
            description='projected comet velocity vector position angle'
            ' (degrees E of N)'
        ),
        "trueanomaly": fields.Float(
            attribute='Found.trueanomaly',
            description='true anomaly based on osculating elements'
            ' (degrees)'
        ),
        "tmtp": fields.Float(
            attribute='Found.tmtp',
            description='T-Tp, time from perihelion, based on osculating'
            ' elements (days)'
        ),
        "filter": fields.String(
            attribute='Obs.filter',
            description='filter name'
        ),
        "exposure": fields.Float(
            attribute='Obs.exposure',
            description='exposure time (s)'
        ),
        "airmass": fields.Float(
            attribute='Obs.airmass',
            description='observation airmass'
        ),
        "productid": fields.String(
            attribute='Obs.productid',
            description='Archive product ID'
        ),
        "instrument": fields.String(
            attribute='Obs.instrument',
            description='Instrument'
        ),
        "archive_url": fields.String(
            attribute='archive_url',
            description='URL to original archive image'
        ),
        "cutout_url": fields.String(
            attribute='cutout_url',
            description='URL to cutout around target ephemeris'
        ),
        "thumbnail_url": fields.String(
            attribute='thumbnail_url',
            description='URL to cutout thumbnail'
        ),
    })

    caught_model: Model = api.model('Caught', {
        'count': fields.Integer(
            description=("Number of observations that caught the target's"
                         " ephemeris position")
        ),
        'job_id': fields.String(
            description='Unique job ID of results'
        ),
        'data': fields.List(fields.Nested(caught_data))
    })


COLUMN_LABELS: Dict[str, Dict[str, Dict[str, Union[str, int]]]] = {
    '/': {
        'designation': {
            'label': 'Designation',
            'description': 'Object designation'
        },
        'jd': {
            'label': 'Date',
            'description': ('Mid-time of the observation as a Julian Date'
                            ' (UT)'),
            'fractionSize': 4
        },
        'ra': {
            'label': 'RA',
            'description': 'Object Right Ascension (deg)',
            'fractionSize': 4
        },
        'dec': {
            'label': 'Dec',
            'description': 'Object Declination (deg)',
            'fractionSize': 4
        },
        'dra': {
            'label': 'd[RA]/dt',
            'description': ('Right Ascension rate of change:'
                            ' dRA/dt cos(Dec) (arcsec/hr)'),
            'fractionSize': 2
        },
        'ddec': {
            'label': 'd[Dec]/dt',
            'description': 'Declination rate of change: dDec/dt (arcsec/hr)',
            'fractionSize': 2
        },
        'unc_a': {
            'label': 'σ(a)',
            'description': 'Error ellipse semi-major axis (arcsec)',
            'fractionSize': 2
        },
        'unc_b': {
            'label': 'σ(b)',
            'description': 'Error ellipse semi-minor axis (arcsec)',
            'fractionSize': 2
        },
        'unc_theta': {
            'label': 'σ(θ)',
            'description': 'Error ellipse position angle (deg)',
            'fractionSize': 0
        },
        'vmag': {
            'label': 'V',
            'description': 'Predicted V-band brightness (mag); For comet ephemerides from JPL, this value is T-mag, if available, otherwise N-mag',
            'fractionSize': 1
        },
        'rh': {
            'label': 'rh',
            'description': 'Heliocentric distance (au)',
            'fractionSize': 3
        },
        'rdot': {
            'label': 'd[rh]/dt',
            'description': 'Heliocentric radial velocity (km/s)',
            'fractionSize': 1
        },
        'delta': {
            'label': 'Δ',
            'description': 'Observer-target distance (au)',
            'fractionSize': 3
        },
        'phase': {
            'label': 'Phase',
            'description': 'Sun-observer-target angle (deg)',
            'fractionSize': 1
        },
        'selong': {
            'label': 'E(⊙)',
            'description': 'Solar elongation (deg)',
            'fractionSize': 0
        },
        'sangle': {
            'label': 'PA(⊙)',
            'description': ('Position angle of projected target-Sun vector,'
                            ' east of Celestial north (deg)'),
            'fractionSize': 0
        },
        'vangle': {
            'label': 'PA(v)',
            'description': ('Position angle of projected target velocity '
                            '  vector, east of Celestial north (deg)'),
            'fractionSize': 0
        },
        'trueanomaly': {
            'label': 'ν',
            'description': ('True anomaly based on osculating orbital'
                            ' elements (deg)'),
            'fractionSize': 1
        },
        'tmtp': {
            'label': 'T-Tₚ',
            'description': ('Time to nearest perihelion based on osculating'
                            ' orbital elements (days)'),
            'fractionSize': 1
        },
        'filter': {
            'label': 'Filter',
            'description': 'Filter name'
        },
        'exposure': {
            'label': 'Exp',
            'description': 'Exposure time',
            'fractionSize': 0
        },
        'airmass': {
            'label': 'Airmass',
            'description': 'Observation airmass',
            'fractionSize': 1
        },
        'productid': {
            'label': 'Product ID',
            'description': 'Unique NEAT product ID'
        },
        'instrument': {
            'label': 'Instrument',
            'description': 'NEAT instrument name'
        },
        'archive_url': {
            'label': 'Archive URL',
            'description': 'Full frame image from data archive'
        },
        'cutout_url': {
            'label': 'Cutout URL',
            'description': 'Cutout image around target ephemeris'
        }
    }
}
