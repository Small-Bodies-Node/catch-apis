"""Task logger.

Logging to `logger` will save messages to the woRQer logs.

"""

import sys
import logging


def setup() -> logging.Logger:
    logger: logging.Logger = logging.Logger('catch-apis tasks')
    logger.setLevel(logging.INFO)

    # In case setup is called multiple times
    if len(logger.handlers) == 0:
        formatter: logging.Formatter = logging.Formatter(
            '%(asctime)10s %(levelname)s: [%(funcName)s] %(message)s',
            "%Y-%m-%d %H:%M:%S")
        console: logging.StreamHandler = logging.StreamHandler(sys.stdout)
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger


logger = setup()
