'''Query DB for ZTF data'''

import os
from typing import Any, List, Dict
from decimal import Decimal
from models.models import Ztf, Found, ZtfCutout, ZtfNight
from .database_provider import DATA_PROVIDER_SESSION

ZTF_CUTOUT_BASE_URL: str = os.getenv('ZTF_CUTOUT_BASE_URL', default='')


def query_ztf_found_data(start_row: int = 0, end_row: int = -1, objid: int = -1) -> Any:
    '''Query DB for ZTF found data'''
    found_ztf_data: Any

    with DATA_PROVIDER_SESSION() as session:
        found_ztf_data = (
            session
            .query(Found, Ztf, ZtfCutout)
            .join(Ztf, Found.obsid == Ztf.obsid)
            # the cutout may not exist, use left outer join:
            .outerjoin(ZtfCutout, Found.foundid == ZtfCutout.foundid)
        )

        if objid > 0:
            found_ztf_data = (
                found_ztf_data
                .filter(Found.objid == objid)
                .order_by(Found.obsjd)
            )

        found_ztf_data = (
            found_ztf_data
            .offset(start_row)
            .limit(500 if end_row == -1 else end_row - start_row)
        )

        serialized_row: Dict[str, Any] = {}
        all_serialized_rows: List[dict] = []
        archive_url: str
        for row in found_ztf_data:
            if row.ZtfCutout is None:
                archive_url = ''
            else:
                archive_url = '/'.join([ZTF_CUTOUT_BASE_URL,
                                        row.ZtfCutout.archivefile])

            filefracday: str = str(row.Ztf.filefracday)
            irsa_url_template: str = (
                'https://irsa.ipac.caltech.edu/ibe/data/ztf/products/sci/'
                '{year}/{monthday}/{fracday}/ztf_{filefracday}_{field:06d}'
                '_{filtercode}_c{ccdid:02d}_o_q{qid:1d}_'
            ).format(year=filefracday[:4], monthday=filefracday[4:8],
                     fracday=filefracday[8:], filefracday=filefracday,
                     field=row.Ztf.field, filtercode=row.Ztf.filtercode,
                     ccdid=row.Ztf.ccdid, qid=row.Ztf.qid)

            serialized_row = {
                "foundid": row.Found.foundid,
                "objid": row.Found.objid,
                "obsjd": row.Found.obsjd,
                "ra": row.Found.ra,
                "dec": row.Found.dec,
                "dra": row.Found.dra,
                "ddec": row.Found.ddec,
                "ra3sig": row.Found.ra3sig,
                "dec3sig": row.Found.dec3sig,
                "vmag": row.Found.vmag,
                "rh": row.Found.rh,
                "rdot": row.Found.rdot,
                "delta": row.Found.delta,
                "phase": row.Found.phase,
                "selong": row.Found.selong,
                "sangle": row.Found.sangle,
                "vangle": row.Found.vangle,
                "trueanomaly": row.Found.trueanomaly,
                "tmtp": row.Found.tmtp,
                "pid": row.Ztf.pid,
                "obsdate": row.Ztf.obsdate,
                "infobits": row.Ztf.infobits,
                "field": row.Ztf.field,
                "ccdid": row.Ztf.ccdid,
                "qid": row.Ztf.qid,
                "rcid": row.Ztf.rcid,
                "fid": row.Ztf.fid,
                "filtercode": row.Ztf.filtercode,
                "expid": row.Ztf.expid,
                "filefracday": row.Ztf.filefracday,
                "seeing": row.Ztf.seeing,
                "airmass": row.Ztf.airmass,
                "moonillf": row.Ztf.moonillf,
                "maglimit": row.Ztf.maglimit,
                "archive_url": archive_url,
                "irsa_sci_url": irsa_url_template + 'sciimg.fits',
                "irsa_diff_url": irsa_url_template + 'scimrefdiffimg.fits.fz'
            }
            # Convert items in binary row to tpython data structures
            for key, val in serialized_row.items():
                if isinstance(val, Decimal):
                    serialized_row[key] = float(val)
                elif isinstance(val, int):
                    serialized_row[key] = int(val)
                else:
                    serialized_row[key] = str(val)
            all_serialized_rows.append(serialized_row)

    return all_serialized_rows


def query_ztf_nights_data(start_row: int = 0, end_row: int = -1, nightid: int = -1,
                          date: str = '') -> Any:
    '''Query DB for ZTF nights'''
    ztf_nights_data: Any

    with DATA_PROVIDER_SESSION() as session:
        ztf_nights_data = session.query(ZtfNight)

        if nightid > 0:
            ztf_nights_data = ztf_nights_data.filter(
                ZtfNight.nightid == nightid)
        elif date != '':
            ztf_nights_data = ztf_nights_data.filter(ZtfNight.date == date)

        ztf_nights_data = (
            ztf_nights_data
            .order_by(ZtfNight.nightid)
            .offset(start_row)
            .limit(500 if end_row == -1 else end_row - start_row)
        )

        serialized_row: Dict[str, Any] = {}
        all_serialized_rows: List[dict] = []
        for row in ztf_nights_data:
            serialized_row = {
                "nightid": row.nightid,
                "date": row.date,
                "exposures": row.exposures,
                "quads": row.quads
            }

            # Convert items in binary row to tpython data structures
            for key, val in serialized_row.items():
                if isinstance(val, Decimal):
                    serialized_row[key] = float(val)
                elif isinstance(val, int):
                    serialized_row[key] = int(val)
                else:
                    serialized_row[key] = str(val)
            all_serialized_rows.append(serialized_row)

    return all_serialized_rows
