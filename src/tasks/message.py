"""Task messages.

Tasks communicate to the user via the `stream` route.  Redis requires
strings for messsages.  So, CATCH-APIs uses JSON-formatted data.
Three keys are currently supported:

    message = {
        'job_prefix': ''  # 8 character job ID prefix
        'message': ''     # text message for the user
        'status': ''      # one of success, error, running, queued
    }

The `tasks.message.Message` class should be used to ensure proper
message formatting.

"""


from typing import Union, Dict
from uuid import UUID
from enum import Enum
import json


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
        Task status.  See ``Status`` for allowed values.

    """

    def __init__(self, job_id: Union[str, UUID],
                 text: str = '',
                 status: Union[str, Status] = Status.NONE):
        self.job_id = job_id
        self.text = text
        self.status = status

    @property
    def job_id(self):
        return self._job_id

    @job_id.setter
    def job_id(self, j: Union[str, UUID]):
        self._job_id = UUID(str(j), version=4)

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, s: Union[str, Status]):
        self._status = Status(s)

    def __str__(self):
        """JSON-formatted string."""
        msg: Dict[str, str] = {
            'job_prefix': self.job_id.hex[:8],
            'message': str(self.text)
        }

        if self.status is not None:
            msg['status'] = self.status.value

        return json.dumps(msg)

    def __repr__(self):
        """String representation."""
        return '<Message: {}>'.format(str(self))
