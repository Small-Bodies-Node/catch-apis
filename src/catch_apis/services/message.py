# Licensed with the 3-clause BSD license.  See LICENSE for details.

"""Task messages.

Tasks communicate to the user via the ``stream`` route.  Redis messages must be
strings.  Therefore, CATCH-APIs publishes messages as JSON-formatted data. Three
keys are currently supported:

    message = {
        'job_prefix': '',  # 8-character job ID prefix
        'text': '',        # text message for the user
        'elapsed': 0,      # number of seconds since query began
        'status': ''       # one of success, error, running, queued
    }

The `tasks.message.Message` class should be used to ensure proper
message formatting.

This module also defines an interface to the task messaging stream via
the Python logging facility.  Use `listen_to_task_messenger` to register
a logging handler with a given job ID.  When info messages are sent to
the logger (e.g., via the catch library), they will be published to the
stream.


Examples
--------
>>> # create unique job id
>>> import uuid
>>> job_id = uuid.uuid4()

>>> # connect the logger and redis messaging stream
>>> listen_for_task_messages(job_id)

>>> # create a message and publish it to the logger and stream
>>> msg = Message(job_id, status='running', text='this job is running')
>>> msg.publish()

>>> # done logging, remove the message listener
>>> stop_listening_for_task_messages(job_id)

"""

import os
import json
import logging
import urllib.parse
from uuid import UUID
from enum import Enum
from time import monotonic

from flask import request

from .queue import RedisConnection
from catch_apis.config.env import ENV


class TaskStatus(Enum):
    """Valid task statuses."""

    NONE = "none"
    SUCCESS = "success"
    ERROR = "error"
    RUNNING = "running"
    QUEUED = "queued"


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

    # Reference time.  This will typically get defined when a task worker starts
    # up, which is what we want.  But in some cases we need to use
    # `Message.reset_t0()` to define a new reference time.
    t0: float = monotonic()

    def __init__(
        self,
        job_id: str | UUID,
        text: str = "",
        status: str | TaskStatus = TaskStatus.NONE,
    ) -> None:
        self.job_id = UUID(str(job_id), version=4)
        self.text = text
        self.status = TaskStatus(status)
        self._redis = RedisConnection()

    @classmethod
    def reset_t0(cls):
        """Reset the reference time."""
        cls.t0 = monotonic()

    @property
    def job_id(self) -> UUID:
        return self._job_id

    @job_id.setter
    def job_id(self, j: str | UUID) -> None:
        self._job_id = UUID(str(j), version=4)

    @property
    def status(self) -> TaskStatus:
        return self._status

    @status.setter
    def status(self, s: str | TaskStatus) -> None:
        self._status = TaskStatus(s)

    @property
    def elapsed(self) -> float:
        """Seconds elapsed since reference time."""
        return round(monotonic() - Message.t0, 1)

    def __str__(self) -> str:
        """JSON-formatted string."""

        msg = {
            "job_prefix": self.job_id.hex[:8],
            "text": str(self.text),
            "elapsed": self.elapsed,
        }

        if self.status is not TaskStatus.NONE:
            msg["status"] = self.status.value

        return json.dumps(msg)

    def __repr__(self) -> str:
        """String representation."""
        return "<Message: {}>".format(str(self))

    def publish(self):
        """Publish this message to the user message stream."""
        self._redis.xadd(
            ENV.REDIS_TASK_MESSAGES,
            {"data": str(self)},
            maxlen=ENV.REDIS_TASK_MESSAGES_MAX_QUEUE_SIZE,
            approximate=True,
        )


class MessageHandler(logging.Handler):
    """Python logging interface to CATCH-APIs task messaging queue.


    Parameters
    ----------
    job_id : string or UUID
        Unique job identifier.

    """

    def __init__(self, job_id: str | UUID, level: int = logging.INFO) -> None:
        self.job_id = UUID(str(job_id), version=4)
        self._redis = RedisConnection()
        super().__init__(level)

    @property
    def job_id(self) -> UUID:
        return self._job_id

    @job_id.setter
    def job_id(self, j: str | UUID) -> None:
        self._job_id = UUID(str(j), version=4)

    def emit(self, record: logging.LogRecord) -> None:
        msg = Message(self.job_id)
        msg.text = record.msg % record.args
        msg.status = TaskStatus.RUNNING
        msg.publish()


def listen_for_task_messages(job_id: str | UUID) -> None:
    """Publish messages for this job ID to the task messaging stream.

    Intended for messages with `status='running'`.


    Parameters
    ----------
    job_id : string or UUID
        Unique job identifier.

    """

    job_id = UUID(str(job_id), version=4)
    logger: logging.Logger = logging.getLogger(f"CATCH-APIs {job_id.hex}")

    # avoid duplicating messages by removing and re-adding the message handler
    handler: logging.Handler
    for handler in logger.handlers:
        logger.removeHandler(handler)

    # logger.setLevel not working for MessageHandler, so must pass log level
    # directly to the handler
    level: int = logging.DEBUG if ENV.DEBUG else logging.INFO
    logger.addHandler(MessageHandler(job_id, level=level))


def stop_listening_for_task_messages(job_id: str | UUID) -> None:
    """Stop publishing messages for this job ID to the task messaging stream.


    Parameters
    ----------
    job_id : string or UUID
        Unique job identifier.

    """

    job_id = UUID(str(job_id), version=4)
    logger: logging.Logger = logging.getLogger(f"CATCH-APIs {job_id.hex}")
    handler: logging.Handler
    for handler in logger.handlers:
        if getattr(handler, "job_id", None) == job_id:
            logger.removeHandler(handler)
            break


def get_message_stream_url() -> str:
    """Get the message stream url."""

    parsed: tuple = urllib.parse.urlsplit(request.url_root)
    message_stream_url: str = urllib.parse.urlunsplit(
        (parsed[0], parsed[1], os.path.join(parsed[2], "stream"), "", "")
    )

    return message_stream_url
