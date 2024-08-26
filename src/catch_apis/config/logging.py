"""CATCH APIs logging."""

import os
import logging
import catch_apis.config.env as ENV


def setup() -> logging.Logger:
    """Set up logging.

    The logger instance is named 'CATCH-APIs' and may be returned with
    ``get_logger``.


    Returns
    -------
    logger : logging.Logger

    """

    logger: logging.Logger = logging.getLogger("CATCH-APIs")

    logger.handlers = []

    logger.setLevel(logging.DEBUG if ENV.DEBUG else logging.INFO)

    # delete any previous handlers
    logger.handlers = []

    formatter: logging.Formatter = logging.Formatter(
        "%(levelname)s %(asctime)s (catch-apis): %(message)s"
    )

    console: logging.StreamHandler = logging.StreamHandler()
    console.setFormatter(formatter)
    logger.addHandler(console)

    # create directories as needed
    if not os.path.exists(ENV.CATCH_APIS_LOG_FILE):
        directories = os.path.dirname(ENV.CATCH_APIS_LOG_FILE).split(os.sep)
        for i in range(len(directories)):
            d = os.sep.join(directories[: i + 1])
            if not os.path.exists(d) and d != "":
                os.mkdir(d)

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

    logger: logging.Logger = logging.getLogger("CATCH-APIs")

    if len(logger.handlers) == 0:
        setup()

    return logger
