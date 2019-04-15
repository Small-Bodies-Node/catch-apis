"""
ZTF route namespace and database tables.
"""

import os
from typing import Dict, Any
from flask_restplus import Namespace, Model, fields
from sqlalchemy import Column, Float, ForeignKey, LargeBinary, String
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from util import FormattedStringOrNone

ZTF_CUTOUT_BASE_URL: str = os.getenv('ZTF_CUTOUT_BASE_URL', default='')

Base = declarative_base()
metadata = Base.metadata


class Ztf(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'ztf'
    obsid = Column(ForeignKey('obs.obsid'), index=True)
    pid = Column(BIGINT(20), primary_key=True)
    nightid = Column(ForeignKey('ztf_nights.nightid'), index=True)
    obsdate = Column(String(64))
    infobits = Column(INTEGER(11))
    field = Column(INTEGER(11))
    ccdid = Column(INTEGER(11))
    qid = Column(INTEGER(11))
    rcid = Column(INTEGER(11))
    fid = Column(INTEGER(11))
    filtercode = Column(String(2))
    expid = Column(INTEGER(11))
    filefracday = Column(BIGINT(20))
    seeing = Column(Float(asdecimal=True))
    airmass = Column(Float(asdecimal=True))
    moonillf = Column(Float(asdecimal=True))
    maglimit = Column(Float(asdecimal=True))
    ztf_nights = relationship('ZtfNights')
    obs = relationship('Obs')


class Obj(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'obj'

    objid = Column(INTEGER(11), primary_key=True)
    desg = Column(String(100), nullable=False)


class Obs(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'obs'

    obsid = Column(INTEGER(11), primary_key=True)
    source = Column(String(32), index=True)
    jd_start = Column(Float)
    jd_stop = Column(Float)
    fov = Column(LargeBinary)


class ZtfNights(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'ztf_nights'

    nightid = Column(INTEGER(11), primary_key=True)
    date = Column(String(64), unique=True)
    exposures = Column(INTEGER(11))
    quads = Column(INTEGER(11))
    retrieved = Column(String(64))


class ZtfPhot(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'ztf_phot'

    foundid = Column(INTEGER(11), primary_key=True)
    dx = Column(Float)
    dy = Column(Float)
    bgap = Column(INTEGER(11))
    bg = Column(Float)
    bg_area = Column(INTEGER(11))
    bg_stdev = Column(Float)
    nap = Column(INTEGER(11))
    rap = Column(LargeBinary)
    flux = Column(LargeBinary)
    m = Column(LargeBinary)
    merr = Column(LargeBinary)
    flag = Column(INTEGER(11))


class ZtfStack(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'ztf_stacks'

    stackid = Column(INTEGER(11), primary_key=True)
    stackfile = Column(String(64))
    stackdate = Column(String(64))


class Eph(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'eph'

    ephid = Column(INTEGER(11), primary_key=True)
    objid = Column(ForeignKey('obj.objid'), index=True)
    jd = Column(Float(asdecimal=True))
    rh = Column(Float(asdecimal=True))
    delta = Column(Float(asdecimal=True))
    ra = Column(Float(asdecimal=True))
    dec = Column(Float(asdecimal=True))
    dra = Column(Float(asdecimal=True))
    ddec = Column(Float(asdecimal=True))
    vmag = Column(Float(asdecimal=True))
    retrieved = Column(String(64))

    obj = relationship('Obj')


class Found(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'found'

    foundid = Column(INTEGER(11), primary_key=True)
    objid = Column(ForeignKey('obj.objid'), index=True)
    obsid = Column(INTEGER(11))
    obsjd = Column(Float(asdecimal=True))
    ra = Column(Float(asdecimal=True))
    dec = Column(Float(asdecimal=True))
    dra = Column(Float(asdecimal=True))
    ddec = Column(Float(asdecimal=True))
    ra3sig = Column(Float(asdecimal=True))
    dec3sig = Column(Float(asdecimal=True))
    vmag = Column(Float(asdecimal=True))
    rh = Column(Float(asdecimal=True))
    rdot = Column(Float(asdecimal=True))
    delta = Column(Float(asdecimal=True))
    phase = Column(Float(asdecimal=True))
    selong = Column(Float(asdecimal=True))
    sangle = Column(Float(asdecimal=True))
    vangle = Column(Float(asdecimal=True))
    trueanomaly = Column(Float(asdecimal=True))
    tmtp = Column(Float(asdecimal=True))

    obj = relationship('Obj')

    def serialize(self: Any) -> Dict[str, str]:
        return {
            "obsid": self.obsid,
            "phase": self.phase
        }


class ZtfCutout(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'ztf_cutouts'

    foundid = Column(ForeignKey('found.foundid'),
                     primary_key=True, nullable=False, index=True)
    stackid = Column(ForeignKey('ztf_stacks.stackid'),
                     primary_key=True, nullable=False, index=True)
    retrieved = Column(String(64))
    archivefile = Column(String(64))
    sciimg = Column(INTEGER(11))
    mskimg = Column(INTEGER(11))
    refimg = Column(INTEGER(11))
    scipsf = Column(INTEGER(11))
    diffimg = Column(INTEGER(11))
    diffpsf = Column(INTEGER(11))
    vangleimg = Column(INTEGER(11))
    sangleimg = Column(INTEGER(11))

    found = relationship('Found')
    ztf_stack = relationship('ZtfStack')


class App:
    api: Namespace = Namespace(
        'Catching moving targets with ZTF',
        path="/ztf",
        description="Zwicky Transient Facility survey metadata and"
        " ZChecker results."
    )

    found_data: Model = api.model('FoundData', {
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
            '{year}/{monthday}/{fracday}/ztf_{Ztf.filefracday}_'
            '{Ztf.field:06d}_{Ztf.filtercode}_c{Ztf.ccdid:02d}_o_'
            'q{Ztf.qid:1d}_sciimg.fits',
            description='IRSA full frame science image URL'
        ),
        "irsa_diff_url": fields.FormattedString(
            'https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/'
            '{year}/{monthday}/{fracday}/ztf_{Ztf.filefracday}_'
            '{Ztf.field:06d}_{Ztf.filtercode}_c{Ztf.ccdid:02d}_o_'
            'q{Ztf.qid:1d}_scimrefdiffimg.fits.fz',
            description='IRSA full frame difference image URL'
        )
    })

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
        "data": fields.List(fields.Nested(found_data)),
        "total": fields.Integer(description='number of returned rows')
    })

    found_objects: Model = api.model('FoundObjectsModel', {
        "data": fields.List(fields.Nested(api.model('ZtfNightsData', {
            "objid": fields.Integer(
                description='unique object identifier'
            ),
            "desg": fields.String(
                description='object designation'
            ),
            "obsjd_min": fields.Float(
                description='first identified observation (Julian date)'
            ),
            "obsjd_max": fields.Float(
                description='last identified observation (Julian date)'
            )
        }))),
        "total": fields.Integer(description='number of returned rows')
    })

    nights: Model = api.model('ZtfNightsModel', {
        "start": fields.Integer(
            description='result start row'
        ),
        "end": fields.Integer(
            description='result end row'
        ),
        "nightid": fields.Integer(
            description='requested night ID (-1 for any)'
        ),
        "date": fields.String(
            description='requested date (empty for any)'
        ),
        "data": fields.List(fields.Nested(api.model('ZtfNightsData', {
            "nightid": fields.Integer(
                description='unique night identifier'
            ),
            "date": fields.String(
                description='date (UT)'
            ),
            "exposures": fields.Integer(
                description='number of exposures'
            ),
            "quads": fields.Integer(
                description='number of CCD quads'
            ),
        }))),
        "total": fields.Integer(description='number of returned rows')
    })
