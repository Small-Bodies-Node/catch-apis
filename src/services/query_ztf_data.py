'''Query DB for ZTF data'''

from typing import List, Dict
import sqlalchemy as sa
from models import ztf
from .database_provider import DATA_PROVIDER_SESSION


def found_objects() -> List[dict]:
    """Return ZTF found object list."""
    query: sa.orm.Query

    with DATA_PROVIDER_SESSION() as session:
        # cast to float or else:
        # TypeError: Object of type 'Decimal' is not JSON serializable
        query = (
            session.query(
                ztf.Found.objid,
                ztf.Obj.desg,
                sa.cast(sa.func.min(ztf.Found.obsjd), sa.Float)
                .label('obsjd_min'),
                sa.cast(sa.func.max(ztf.Found.obsjd), sa.Float)
                .label('obsjd_max')
            )
            .join(ztf.Obj, ztf.Obj.objid == ztf.Found.objid)
            .group_by(ztf.Found.objid)
            .order_by(ztf.Obj.desg + 0, ztf.Obj.desg)
        )

    # unpack into list of dictionaries for marshalling
    rows: List[dict] = []
    for row in query:
        rows.append(row._asdict())

    return rows


def found(start_row: int = 0, end_row: int = -1, objid: int = -1,
          nightid: int = -1, maglimit: float = 0,
          seeing: float = 0, foundid: int = -1) -> List[dict]:
    '''Query DB for ZTF found data.'''
    query: sa.orm.Query

    print("\n\n>>>>>>>>>>>>>>>\n\n")

    with DATA_PROVIDER_SESSION() as session:
        query = (
            session
            .query(
                ztf.Found,
                ztf.Ztf,
                ztf.ZtfCutout,
                sa.func.substr(sa.cast(ztf.Ztf.filefracday, sa.String), 1, 4)
                .label('year'),
                sa.func.substr(sa.cast(ztf.Ztf.filefracday, sa.String), 5, 4)
                .label('monthday'),
                sa.func.substr(sa.cast(ztf.Ztf.filefracday, sa.String), 9)
                .label('fracday')
            )
            .join(ztf.Ztf, ztf.Found.obsid == ztf.Ztf.obsid)
            # the cutout may not exist, use left outer join:
            .outerjoin(
                ztf.ZtfCutout,
                ztf.Found.foundid == ztf.ZtfCutout.foundid
            )
        )

        print("\n\n>>>>>>> 2 >>>>>>>>\n\n")

        if maglimit > 0:
            query = query.filter(ztf.Ztf.maglimit > maglimit)

        if nightid > 0:
            query = query.filter(ztf.Ztf.nightid == nightid)

        if seeing > 0:
            query = query.filter(ztf.Ztf.seeing < seeing)

        if objid > 0:
            query = (
                query.filter(ztf.Found.objid == objid)
                .order_by(ztf.Found.obsjd)
            )

        if foundid > 0:
            query = query.filter(ztf.Found.foundid == foundid)
        else:
            query = (
                query.offset(start_row)
                .limit(500 if end_row == -1 else end_row - start_row)
            )

    # unpack into list of dictionaries for marshalling
    rows: List[dict] = []
    for row in query:
        rows.append(row._asdict())

    return rows


def nights(start_row: int = 0, end_row: int = -1, nightid: int = -1,
           date: str = '') -> List[dict]:
    '''Query DB for ZTF nights'''
    query: sa.orm.Query

    with DATA_PROVIDER_SESSION() as session:
        query = session.query(ztf.ZtfNights)

        if nightid > 0:
            query = query.filter(ztf.ZtfNights.nightid == nightid)
        elif date != '':
            query = query.filter(ztf.ZtfNights.date == date)

        query = (
            query.order_by(ztf.ZtfNights.nightid.desc())
            .offset(start_row)
            .limit(500 if end_row == -1 else end_row - start_row)
        )

    # unpack into list of dictionaries for marshalling
    rows: List[dict] = []
    for row in query:
        rows.append(row.__dict__)

    return rows


def column_labels(route: str) -> Dict[str, Dict[str, str]]:
    """Column labels for query results."""
    return COLUMN_LABELS.get(route, {})


COLUMN_LABELS: Dict[str, Dict[str, Dict[str, str]]] = {
    '/found': {
        'foundid': {
            'label': 'Found ID',
            'description': ('Internal database unique ID for an observation'
                            ' of an object')
        },
        'objid': {
            'label': 'Object ID',
            'description': 'Internal database unique object ID'
        },
        'obsjd': {
            'label': 'Date',
            'description': ('Mid-time of the observation as a Julian Date'
                            ' (UT)')
        },
        'ra': {
            'label': 'RA',
            'description': 'Object Right Ascension (deg)'
        },
        'dec': {
            'label': 'Dec',
            'description': 'Object Declination (deg)'
        },
        'dra': {
            'label': 'dRA',
            'description': ('Right Ascension rate of change:'
                            ' dRA/dt cos(Dec) ("/hr)')
        },
        'ddec': {
            'label': 'dDec',
            'description': 'Declination rate of change: dDec/dt ("/hr)'
        },
        'ra3sig': {
            'label': 'RA 3σ',
            'description': 'Right Ascension 3σ uncertainty (")'
        },
        'dec3sig': {
            'label': 'Dec 3σ',
            'description': 'Declination 3σ uncertainty (")'
        },
        'vmag': {
            'label': 'V',
            'description': 'Predicted V-band brightness (mag)'
        },
        'rh': {
            'label': 'rh',
            'description': 'Heliocentric distance (au)'
        },
        'rdot': {
            'label': 'ṙh',
            'description': 'Heliocentric radial velocity (km/s)'
        },
        'delta': {
            'label': 'Δ',
            'description': 'Observer-target distance (au)'
        },
        'phase': {
            'label': 'Phase',
            'description': 'Sun-observer-target angle (deg)'
        },
        'selong': {
            'label': 'E(⊙)"',
            'description': 'Solar elongation (deg)'
        },
        'sangle': {
            'label': 'PA(⊙)',
            'description': ('Position angle of projected target-Sun vector,'
                            ' east of Celestial north (deg)')
        },
        'vangle': {
            'label': 'PA(v)',
            'description': ('Position angle of projected target velocity '
                            '  vector, east of Celestial north (deg)')
        },
        'trueanomaly': {
            'label': 'ν',
            'description': ('True anomaly based on osculating orbital'
                            ' elements (deg)')
        },
        'tmtp': {
            'label': 'T-Tₚ',
            'description': ('Time to nearest perihelion based on osculating'
                            ' orbital elements (days)')
        },
        'pid': {
            'label': 'Product',
            'description': 'ZTF unique product ID'
        },
        'obsdate': {
            'label': 'Date',
            'description': 'Mid-time of the observation'
        },
        'infobits': {
            'label': 'Infobits',
            'description': 'ZTF pipeline infobits'
        },
        'field': {
            'label': 'Field',
            'description': 'ZTF field ID'
        },
        'ccdid': {
            'label': 'CCD',
            'description': 'ZTF CCD ID (1...16)'
        },
        'qid': {
            'label': 'Quad',
            'description': 'ZTF CCD quadrant ID (1...4)'
        },
        'rcid': {
            'label': 'RC',
            'description': 'Readout channel ID (0...63)'
        },
        'fid': {
            'label': 'Filter ID',
            'description': 'ZTF filter ID'
        },
        'filtercode': {
            'label': 'Filter',
            'description': 'ZTF abbreviated filter name'
        },
        'expid': {
            'label': 'Exp',
            'description': 'ZTF exposure ID'
        },
        'filefracday': {
            'label': 'Filefracday',
            'description': 'Fraction time of day of expsoure (UT)'
        },
        'seeing': {
            'label': 'Seeing',
            'description': 'Seeing, i.e., FWHM of point sources (")'
        },
        'airmass': {
            'label': 'Airmass',
            'description': 'Observation airmass'
        },
        'moonillf': {
            'label': 'Moon frac',
            'description': 'Moon illuminated fraction'
        },
        'maglimit': {
            'label': 'Mag limit',
            'description': '5σ point-source senstivity (mag)'
        },
        'archive_url': {
            'label': 'Archive URL',
            'description': 'Local archive URL'
        },
        'irsa_sci_url': {
            'label': 'Sci URL',
            'description': 'Full-frame science URL at IRSA'
        },
        'irsa_diff_url': {
            'label': 'Diff URL',
            'description': 'Full-frame differenced image URL at IRSA'
        }
    }
}
