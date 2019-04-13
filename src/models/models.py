"""
These models were generated using script _generate_models.sh
"""

from typing import Dict, Any
from flask_restplus import fields
from sqlalchemy import Column, Float, ForeignKey, LargeBinary, String, Table
from sqlalchemy.dialects.mysql import BIGINT, INTEGER
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
metadata = Base.metadata


ztf_found_result = {
    "foundid": fields.Integer(
        description='unique identifier for found object observation'
    ),
    "objid": fields.Integer(
        description='unique identifier for object'
    ),
    "obsjd": fields.Float(
        description='mid-point of the observation and epoch for ephemeris'
        ' (Julian date)'
    ),
    "ra": fields.Float(
        description='ephemeris Right Ascension (deg)'
    ),
    "dec": fields.Float(
        description='ephemeris Declination (deg)'
    ),
    "dra": fields.Float(
        description='RA * cos(Dec) rate of change (arcsec/hr)'
    ),
    "ddec": fields.Float(
        description='Declination rate of change (arcsec/hr)'
    ),
    "ra3sig": fields.Float(
        description='Right Ascension 3σ uncertainty (arcsec)'
    ),
    "dec3sig": fields.Float(
        description='Declination 3σ uncertainty (arcsec)'
    ),
    "vmag": fields.Float(
        description='brightness estimate (magnitude)'
    ),
    "rh": fields.Float(
        description='heliocentric distance (au)'
    ),
    "rdot": fields.Float(
        description='heliocentric distance rate of change (km/s)'
    ),
    "delta": fields.Float(
        description='observer-target distance (au)'
    ),
    "phase": fields.Float(
        description='phase angle (degrees)'
    ),
    "selong": fields.Float(
        description='solar elongation (degrees)'
    ),
    "sangle": fields.Float(
        description='projected comet-sun vector position angle (degrees E of N)'
    ),
    "vangle": fields.Float(
        description='projected comet velocity vector position angle'
        ' (degrees E of N)'
    ),
    "trueanomaly": fields.Float(
        description='true anomaly based on osculating elements (degrees)'
    ),
    "tmtp": fields.Float(
        description='T-Tp, time from perihelion, based on osculating elements'
        ' (days)'
    ),
    "pid": fields.Integer(
        description='ZTF unique science product ID'
    ),
    "obsdate": fields.String(
        description='observation mid-time (UT)'
    ),
    "infobits": fields.Integer(
        description='info bit flags, see Section 10.4 of the ZTF Science Data'
        ' System'
    ),
    "field": fields.Integer(
        description='ZTF field number'
    ),
    "ccdid": fields.Integer(
        description='detector chip ID (1, ...16), see Fig. 1 of ZTF Science'
        ' Data System'
    ),
    "qid": fields.Integer(
        description='CCD quadrant ID (1, 2, 3, 4), see Fig. 1 of ZTF Science'
        ' Data System'
    ),
    "rcid": fields.Integer(
        description='readout channel ID (0, ...63)'
    ),
    "fid": fields.Integer(
        description='filter ID'
    ),
    "filtercode": fields.String(
        description='abbreviated filter name: zr, zg, zi'
    ),
    "expid": fields.Integer(
        description='exposure ID'
    ),
    "filefracday": fields.Integer(
        description='fractional time of day of exposure (UT)'
    ),
    "seeing": fields.Float(
        description='seeing FWHM (arcsec)'
    ),
    "airmass": fields.Float(
        description='telescope airmass'
    ),
    "moonillf": fields.Float(
        description='Moon illuminated fraction'
    ),
    "maglimit": fields.Float(
        description='magnitude limit'
    ),
    "archive_url": fields.String(
        description='FITS cutout from local archive'
    ),
    "irsa_sci_url": fields.String(
        description='IRSA full frame science image URL'
    ),
    "irsa_diff_url": fields.String(
        description='IRSA full frame difference image URL'
    )
}


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
    ztf_night = relationship('ZtfNight')
    ob = relationship('Ob')

    def serialize(self: Any) -> Dict[str, str]:
        return {
            "obsid": self.obsid,
            "pid": self.pid,
            "nightid": self.nightid,
            "obsdate": self.obsdate
        }


class Obj(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'obj'

    objid = Column(INTEGER(11), primary_key=True)
    desg = Column(String(100), nullable=False)


class Ob(Base):
    """TODO DOCSTRING"""
    __tablename__ = 'obs'

    obsid = Column(INTEGER(11), primary_key=True)
    source = Column(String(32), index=True)
    jd_start = Column(Float)
    jd_stop = Column(Float)
    fov = Column(LargeBinary)


t_ztf_found = Table(
    'ztf_found', metadata,
    Column('obsid', INTEGER(11)),
    Column('foundid', INTEGER(11)),
    Column('objid', INTEGER(11)),
    Column('obsjd', Float(asdecimal=True)),
    Column('ra', Float(asdecimal=True)),
    Column('dec', Float(asdecimal=True)),
    Column('dra', Float(asdecimal=True)),
    Column('ddec', Float(asdecimal=True)),
    Column('ra3sig', Float(asdecimal=True)),
    Column('dec3sig', Float(asdecimal=True)),
    Column('vmag', Float(asdecimal=True)),
    Column('rh', Float(asdecimal=True)),
    Column('rdot', Float(asdecimal=True)),
    Column('delta', Float(asdecimal=True)),
    Column('phase', Float(asdecimal=True)),
    Column('selong', Float(asdecimal=True)),
    Column('sangle', Float(asdecimal=True)),
    Column('vangle', Float(asdecimal=True)),
    Column('trueanomaly', Float(asdecimal=True)),
    Column('tmtp', Float(asdecimal=True)),
    Column('pid', BIGINT(20)),
    Column('nightid', INTEGER(11)),
    Column('obsdate', String(64)),
    Column('infobits', INTEGER(11)),
    Column('field', INTEGER(11)),
    Column('ccdid', INTEGER(11)),
    Column('qid', INTEGER(11)),
    Column('rcid', INTEGER(11)),
    Column('fid', INTEGER(11)),
    Column('filtercode', String(2)),
    Column('expid', INTEGER(11)),
    Column('filefracday', BIGINT(20)),
    Column('seeing', Float(asdecimal=True)),
    Column('airmass', Float(asdecimal=True)),
    Column('moonillf', Float(asdecimal=True)),
    Column('maglimit', Float(asdecimal=True))
)


class ZtfNight(Base):
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


t_ztf_stale_files = Table(
    'ztf_stale_files', metadata,
    Column('path', String(256)),
    Column('file', String(256))
)


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
