"""Tasks for CATCH searches."""
import uuid

from redis import Redis, StrictRedis

from tasks import RQueues
from services.database_provider import catch_manager

strict_redis: Redis = StrictRedis()


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

    with catch_manager(save_log=True) as catch:
        catch.query(desg, job_id, source=source,
                    cached=cached, eph_source='jpl')

    strict_redis.publish(RQueues.FINISH_JOBS, job_id.hex)
