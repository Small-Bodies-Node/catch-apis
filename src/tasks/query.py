"""Tasks for CATCH searches."""
import uuid
import logging

from redis import Redis, StrictRedis
from sbsearch.exceptions import SBSException
from catch.schema import Found, Obs, Obj, NEATPalomar, NEATMauiGEODSS
from catch.catch import CatchException

from services.database_provider import catch_manager
from tasks import RQueues, images
from tasks.message import Message, listen_to_task_messenger
from tasks.logger import logger
from util import desg_to_prefix

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

    msg: Message = Message(job_id, status='running',
                           text='Starting moving target query.')
    strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))
    listen_to_task_messenger(job_id)

    try:
        with catch_manager(save_log=True) as catch:
            # send catch logging to the task message stream
            count: int = catch.query(desg, job_id, source=source,
                                     cached=cached, eph_source='jpl')

        if count > 0:
            cutout_moving_targets(job_id, overwrite=False, sub_task=True)

        msg.status = 'success'
        msg.text = 'Task complete.'
    except (CatchException, SBSException) as e:
        logger.error(e, stack_info=True)
        msg.status = 'error'
        msg.text = str(e)
    except:
        logger.error("An unexpected error occurred.", exc_info=True)
        msg.status = 'error'
        msg.text = 'An unexpected error occurred.  If this happens again contact us.'
    finally:
        strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))


def cutout_moving_targets(job_id: uuid.UUID, overwrite: bool = False,
                          sub_task: bool = False) -> None:
    """Cutout and thumbnail moving targets for local CATCH surveys.

    Parameters
    ----------
    job_id : uuid.UUID
        Unique ID for job.

    overwrite : bool, optional
        Overwrite existing files.

    sub_task : bool, optional
        ``True`` if this is part of another task, which prevents
        publishing a success message.

    """

    msg: Message = Message(job_id, status='running',
                           text='Generating cutouts.')
    strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))

    n_cutouts: int = 0
    try:
        with catch_manager(save_log=True) as catch:
            rows: list = catch.caught(job_id)

            # target cutouts
            found: Found
            obs: Obs
            obj: Obj
            for found, obs, obj in rows:
                prefix: str = '{}_'.format(desg_to_prefix(obj.desg))
                if isinstance(obs, (NEATPalomar, NEATMauiGEODSS)):
                    n_cutouts += images.neat_cutout(
                        obs.productid, job_id, found.ra, found.dec,
                        prefix=prefix, overwrite=overwrite, thumbnail=True,
                        preview=True)

        if not sub_task:
            msg.status = 'success'
        msg.text = 'Generated {} cutout{}.'.format(
            n_cutouts, '' if n_cutouts == 1 else 's')
    except (CatchException, SBSException) as e:
        logger.error(e, stack_info=True)
        msg.status = 'error'
        msg.text = str(e)
    except:
        logger.error("An unexpected error occurred.", exc_info=True)
        msg.status = 'error'
        msg.text = 'An unexpected error occurred.  If this happens again contact us.'
    finally:
        strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))
