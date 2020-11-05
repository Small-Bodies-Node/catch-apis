"""Task messages.

Tasks communicate to the user via the `stream` route.  Redis requires
strings for messsages.  So, CATCH-APIs uses JSON-formatted data.
Three keys are currently supported:

    message = {
        'job_prefix': ''  # 8-character job ID prefix
        'text': ''        # text message for the user
        'status': ''      # one of success, error, running, queued
    }

The `tasks.message.Message` class should be used to ensure proper
message formatting.

This module also defines an interface to the task messaging stream via
the Python logging facility.  Use `listen_to_task_messenger` to
register a logging handler with a given job ID.  When info messages
are sent to the logger (e.g., via the catch library), they will be
published to the stream.

"""


from typing import Union, Dict
from uuid import UUID
from enum import Enum
import logging
import json

from redis import Redis, StrictRedis

from . import RQueues


class Status(Enum):
    """Valid task statuses."""
    NONE = 'none'
    SUCCESS = 'success'
    ERROR = 'error'
    RUNNING = 'running'
    QUEUED = 'queued'


class Message:
    """CATCH-APIs task message container.


    Parameters
    ----------
    job_id : string or UUID
        Unique job identifier.

    text : string, optional
        Text message for the user.

    status : string or Status
        Task status.  See `Status` for allowed values.

    """

    def __init__(self, job_id: Union[str, UUID],
                 text: str = '',
                 status: Union[str, Status] = Status.NONE):
        self.job_id = job_id
        self.text = text
        self.status = status

    @property
    def job_id(self) -> UUID:
        return self._job_id

    @job_id.setter
    def job_id(self, j: Union[str, UUID]) -> None:
        self._job_id = UUID(str(j), version=4)

    @property
    def status(self) -> Status:
        return self._status

    @status.setter
    def status(self, s: Union[str, Status]) -> None:
        self._status = Status(s)

    def __str__(self) -> str:
        """JSON-formatted string."""
        msg: Dict[str, str] = {
            'job_prefix': self.job_id.hex[:8],
            'text': str(self.text)
        }

        if self.status is not Status.NONE:
            msg['status'] = self.status.value

        return json.dumps(msg)

    def __repr__(self) -> str:
        """String representation."""
        return '<Message: {}>'.format(str(self))


class MessageHandler(logging.Handler):
    """Python logging interface to CATCH-APIs task messaging queue.


    Parameters
    ----------
    job_id : string or UUID
        Unique job identifier.

    """

    def __init__(self, job_id: Union[str, UUID], level: int = logging.INFO) -> None:
        self.job_id = job_id
        self.strict_redis: Redis = StrictRedis()
        logging.Handler.__init__(self, level)

    @property
    def job_id(self) -> UUID:
        return self._job_id

    @job_id.setter
    def job_id(self, j: Union[str, UUID]) -> None:
        self._job_id = UUID(str(j), version=4)

    def emit(self, record: logging.LogRecord) -> None:
        msg: Message = Message(self.job_id)
        msg.text = record.msg
        msg.status = Status.RUNNING
        self.strict_redis.publish(RQueues.TASK_MESSAGES, str(msg))


def listen_to_task_messenger(job_id: Union[str, UUID]) -> None:
    """Publish messages for this job ID to the task messaging stream.

    Intended for messages with `status='running'`.


    Parameters
    ----------
    job_id : string or UUID
        Unique job identifier.

    """

    job_id = UUID(str(job_id), version=4)
    logger = logging.getLogger('CATCH-APIs {}'.format(job_id.hex))
    logger.setLevel(logging.INFO)
    logger.addHandler(MessageHandler(job_id))
