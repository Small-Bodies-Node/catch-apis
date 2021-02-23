"""CATCH APIs logging."""

import logging
from .env import ENV


def setup() -> logging.Logger:
    """Set up logging.

    The logger instance is named 'CATCH-APIs' and may be returned with
    ``get_logger``.


    Returns
    -------
    logger : logging.Logger

    """

    logger: logging.Logger = logging.getLogger('CATCH-APIs')

    logger.handlers = []

    logger.setLevel(logging.INFO)

    # delete any previous handlers
    logger.handlers = []

    formatter: logging.Formatter = logging.Formatter(
        '%(levelname)s %(asctime)s (catch-apis): %(message)s')

    console: logging.StreamHandler = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    logfile: logging.FileHandler = logging.FileHandler(ENV.CATCH_APIS_LOG_FILE)
    logfile.setFormatter(formatter)
    logger.addHandler(logfile)

    return logger


def get_logger() -> logging.Logger:
    """Return the logger.

    This is a convenience function that will call ``setup``, as needed.


    Returns
    -------
    logger : logging.Logger

    """

    logger: logging.Logger = logging.getLogger('CATCH-APIs')

    if len(logger.handlers) == 0:
        setup()

    return logger
