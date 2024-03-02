"""Query status enumerated list."""

import enum


class QueryStatus(enum.Enum):
    UNDEFINED = 'undefined'
    SUCCESS = 'success'
    QUEUED = 'queued'
    QUEUEFULL = 'queue full'
    FAILED = 'failed'
