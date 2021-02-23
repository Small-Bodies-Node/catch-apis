"""Environment variables."""

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True, verbose=True)


class ENV():
    """ Class to store all env variables used in app """

    # String properties
    TEST_DATA_PATH: str = os.path.abspath(str(
        os.getenv("TEST_DATA_PATH", "./data/test")))
    DEPLOYMENT_TIER: str = os.getenv("DEPLOYMENT_TIER", "LOCAL")
    DB_HOST: str = str(os.getenv("DB_HOST", ""))
    DB_DIALECT: str = str(os.getenv("DB_DIALECT", "sqlite"))
    DB_USERNAME: str = str(os.getenv("DB_USERNAME", ""))
    DB_PASSWORD: str = str(os.getenv("DB_PASSWORD", ""))
    DB_DATABASE: str = str(os.getenv("DB_DATABASE", "default.db"))
    BASE_HREF: str = str(os.getenv("BASE_HREF", "/"))
    CATCH_LOG_FILE: str = str(os.path.abspath(
        os.getenv('CATCH_LOG_FILE', './logging/catch.log')))
    CATCH_APIS_LOG_FILE: str = str(os.path.abspath(
        os.getenv('CATCH_APIS_LOG_FILE', './logging/catch-apis.log')))

    # Numeric properties
    LIVE_GUNICORN_INSTANCES: int = int(
        os.getenv("LIVE_GUNICORN_INSTANCES", -1))
    API_PORT: int = int(
        os.getenv("API_PORT", 5001))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", 6379))
    REDIS_MAX_QUEUE_SIZE: int = int(os.getenv("REDIS_MAX_QUEUE_SIZE", 100))
    STREAM_TIMEOUT: int = int(os.getenv("STREAM_TIMEOUT", 60))

    # Boolean Properties
    IS_DAEMON: bool = (os.getenv("IS_DAEMON", "false").lower()
                       not in ['false', '0'])
    DEBUG: bool = os.getenv("DEBUG", "false").lower() not in ['false', '0']
