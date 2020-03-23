"""Tasks for CATCH searches."""
import uuid
import logging

from redis import Redis, StrictRedis
from sbsearch.exceptions import SBSException
from catch.schema import Found, Obs, Obj, NEATPalomar, NEATMauiGEODSS

from services.database_provider import catch_manager
from tasks import RQueues, images
from util import desg_to_prefix

strict_redis: Redis = StrictRedis()
logger: logging.Logger = logging.getLogger(__name__)


def catch_moving_target(desg: str, source: str, cached: bool,
                        job_id: uuid.UUID) -> None:
    """Search for target in CATCH surveys.

    Parameters
    ----------
    desg : string
        Target designation.

    source : string
        Name of observation source to search or ``'any'``.

    cached : bool
        `True` to use cached results.

    job_id : uuid.UUID
        Unique ID for job.

    """

    try:
        with catch_manager(save_log=True) as catch:
            catch.query(desg, job_id, source=source,
                        cached=cached, eph_source='jpl')
        cutout_moving_targets(job_id, overwrite=False)
    except (RuntimeError, SBSException) as e:
        logger.error(str(e))
    except:
        logger.error("Some error occurred. Perhaps this objid does not exist")

    strict_redis.publish(RQueues.FINISH_JOBS, job_id.hex)


def cutout_moving_targets(job_id: uuid.UUID, overwrite: bool = False) -> None:
    """Cutout and thumbnail moving targets for local CATCH surveys.

    Parameters
    ----------
    job_id : uuid.UUID
        Unique ID for job.

    overwrite : bool, optional
        Overwrite existing files.

    """

    with catch_manager(save_log=True) as catch:
        rows: list = catch.caught(job_id)

        # target cutouts
        found: Found
        obs: Obs
        obj: Obj
        for found, obs, obj in rows:
            prefix: str = '{}_'.format(desg_to_prefix(obj.desg))
            if isinstance(obs, (NEATPalomar, NEATMauiGEODSS)):
                images.neat_cutout(obs.productid, job_id, found.ra, found.dec,
                                   prefix=prefix, overwrite=overwrite,
                                   thumbnail=True)

    strict_redis.publish(RQueues.FINISH_JOBS, job_id.hex)
