import os
from flask_restplus import Namespace, Model, fields
from util import FormattedStringOrNone

ZTF_CUTOUT_BASE_URL: str = os.getenv('ZTF_CUTOUT_BASE_URL', default='')


class ZTF:
    api: Namespace = Namespace(
        'Catching moving targets with ZTF',
        path="/ztf",
        description="Zwicky Transient Facility survey metadata and"
        " ZChecker results."
    )

    found: Model = api.model('FoundModel', {
        "start": fields.Integer(
            description='result start row'
        ),
        "end": fields.Integer(
            description='result end row'
        ),
        "maglimit": fields.Float(
            description='requested magnitude limit (0 for any)'
        ),
        "objid": fields.Integer(
            description='requested object ID (-1 for any)'
        ),
        "nightid": fields.Integer(
            description='requested night ID (-1 for any)'
        ),
        "seeing": fields.Float(
            description='requested seeing limit (0 for any)'
        ),
        "data": fields.List(fields.Nested(api.model('FoundData', {
            "foundid": fields.Integer(
                attribute='Found.foundid',
                description='unique identifier for found object observation'
            ),
            "objid": fields.Integer(
                attribute='Found.objid',
                description='unique identifier for object'
            ),
            "obsjd": fields.Float(
                attribute='Found.obsjd',
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
            "ra3sig": fields.Float(
                attribute='Found.ra3sig',
                description='Right Ascension 3σ uncertainty (arcsec)'
            ),
            "dec3sig": fields.Float(
                attribute='Found.dec3sig',
                description='Declination 3σ uncertainty (arcsec)'
            ),
            "vmag": fields.Float(
                attribute='Found.vmag',
                description='brightness estimate (magnitude)'
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
            "pid": fields.Integer(
                attribute='Ztf.pid',
                description='ZTF unique science product ID'
            ),
            "obsdate": fields.String(
                attribute='Ztf.obsdate',
                description='observation mid-time (UT)'
            ),
            "infobits": fields.Integer(
                attribute='Ztf.infobits',
                description='info bit flags, see Section 10.4 of the ZTF'
                ' Science Data System'
            ),
            "field": fields.Integer(
                attribute='Ztf.field',
                description='ZTF field number'
            ),
            "ccdid": fields.Integer(
                attribute='Ztf.ccdid',
                description='detector chip ID (1, ...16), see Fig. 1 of ZTF'
                ' Science Data System'
            ),
            "qid": fields.Integer(
                attribute='Ztf.qid',
                description='CCD quadrant ID (1, 2, 3, 4), see Fig. 1 of ZTF'
                ' Science Data System'
            ),
            "rcid": fields.Integer(
                attribute='Ztf.rcid',
                description='readout channel ID (0, ...63)'
            ),
            "fid": fields.Integer(
                attribute='Ztf.fid',
                description='filter ID'
            ),
            "filtercode": fields.String(
                attribute='Ztf.filtercode',
                description='abbreviated filter name: zr, zg, zi'
            ),
            "expid": fields.Integer(
                attribute='Ztf.expid',
                description='exposure ID'
            ),
            "filefracday": fields.Integer(
                attribute='Ztf.filefracday',
                description='fractional time of day of exposure (UT)'
            ),
            "seeing": fields.Float(
                attribute='Ztf.seeing',
                description='seeing FWHM (arcsec)'
            ),
            "airmass": fields.Float(
                attribute='Ztf.airmass',
                description='telescope airmass'
            ),
            "moonillf": fields.Float(
                attribute='Ztf.moonillf',
                description='Moon illuminated fraction'
            ),
            "maglimit": fields.Float(
                attribute='Ztf.maglimit',
                description='magnitude limit'
            ),
            "archive_url": FormattedStringOrNone(
                ZTF_CUTOUT_BASE_URL + '{archivefile}',
                description='FITS cutout from local archive'
            ),
            "irsa_sci_url": fields.FormattedString(
                'https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/'
                '{year}/{monthday}/{fracday}/ztf_{Ztf.filefracday}_{Ztf.field:06d}'
                '_{Ztf.filtercode}_c{Ztf.ccdid:02d}_o_q{Ztf.qid:1d}_sciimg.fits',
                description='IRSA full frame science image URL'
            ),
            "irsa_diff_url": fields.FormattedString(
                'https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/'
                '{year}/{monthday}/{fracday}/ztf_{Ztf.filefracday}_{Ztf.field:06d}'
                '_{Ztf.filtercode}_c{Ztf.ccdid:02d}_o_q{Ztf.qid:1d}_scimrefdiffimg'
                '.fits.fz',
                description='IRSA full frame difference image URL'
            )
        }))),
        "total": fields.Integer(description='number of returned rows')
    })
