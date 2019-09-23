'''Catch NEAT data'''

import os
from typing import List, Dict, Any
from catch import Catch, Config
from catch.schema import Caught, CatchQueries, Obs, Found, Obj
import models
from .database_provider import DATA_PROVIDER_SESSION, db_engine_URI

CATCH_LOG: str = os.getenv('CATCH_LOG', default='/dev/null')
CATCH_ARCHIVE_PATH: str = os.getenv('CATCH_ARCHIVE_PATH', default='/dev/null')
CATCH_CUTOUT_PATH: str = os.getenv('CATCH_CUTOUT_PATH', default='/dev/null')


def query(sessionid: str = '', designation: str = '') -> int:
    """Execute NEAT query and return query ID."""

    opts: dict = {
        'database': db_engine_URI,
        'log': CATCH_LOG,
        'archive path': CATCH_ARCHIVE_PATH,
        'cutout path': CATCH_CUTOUT_PATH
    }
    config: Config = Config(**opts)
    with Catch(config, sessionid=sessionid, save_log=True) as catch:
        queryid: int = catch.query(designation, source='jpl')
        catch.cutouts(queryid)

    return queryid


def caught(sessionid: str = '', queryid: int = 0) -> List[dict]:
    '''Query DB for ZTF found data.'''
    data: List[Any]

    print("\n\n>>>>>>>>>>>>>>>\n\n")

    with DATA_PROVIDER_SESSION() as session:
        data = (session.query(Caught, CatchQueries, Obs, Found, Obj)
                .join(CatchQueries, Caught.queryid == CatchQueries.queryid)
                .join(Obs, Caught.obsid == Obs.obsid)
                .join(Found, Caught.foundid == Found.foundid)
                .join(Obj, Found.objid == Obj.objid)
                .filter(CatchQueries.sessionid == sessionid)
                .filter(CatchQueries.queryid == int(queryid)))

        # make the data persist outside of the session
        session.expunge_all()

        print("\n\n>>>>>>> 2 >>>>>>>>\n\n")

    # unpack into list of dictionaries for marshalling
    rows: List[dict] = []
    for row in data:
        rows.append(row._asdict())
        rows[-1]['cutout_path'] = (
            '{}/{}/{}_cutout.fits'
            .format(sessionid, str(queryid), row.Obs.productid))

    return rows


def column_labels(route: str) -> Dict[str, Dict[str, str]]:
    """Column labels for query results."""
    return models.neat.COLUMN_LABELS.get(route, {})
