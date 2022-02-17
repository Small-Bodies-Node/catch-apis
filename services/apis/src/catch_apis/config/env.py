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
    DB_DIALECT: str = str(os.getenv("DB_DIALECT", "postgresql"))
    DB_USERNAME: str = str(os.getenv("DB_USERNAME", ""))
    DB_PASSWORD: str = str(os.getenv("DB_PASSWORD", ""))
    DB_DATABASE: str = str(os.getenv("DB_DATABASE", "catch"))
    BASE_HREF: str = str(os.getenv("BASE_HREF", "/"))
    REDIS_HOST: str = str(os.getenv("REDIS_HOST", 'localhost'))
    REDIS_TASK_MESSAGES: str = str(os.getenv("REDIS_TASK_MESSAGES", ''))
    REDIS_JOBS: str = str(os.getenv("REDIS_JOBS", ''))
    CATCH_LOG_FILE: str = str(os.path.abspath(
        os.getenv('CATCH_LOG_FILE', './logging/catch.log')))
    CATCH_APIS_LOG_FILE: str = str(os.path.abspath(
        os.getenv('CATCH_APIS_LOG_FILE', './logging/catch-apis.log')))

    # Numeric properties
    GUNICORN_WORKER_INSTANCES: int = int(
        os.getenv("GUNICORN_WORKER_INSTANCES", '-1'))
    GUNICORN_FLASK_INSTANCES: int = int(
        os.getenv("GUNICORN_FLASK_INSTANCES", '-1'))
    API_PORT: int = int(os.getenv("API_PORT", '5000'))
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", '6379'))
    REDIS_MAX_QUEUE_SIZE: int = int(os.getenv("REDIS_MAX_QUEUE_SIZE", '100'))
    STREAM_TIMEOUT: int = int(os.getenv("STREAM_TIMEOUT", '60'))

    # Boolean Properties
    DEBUG: bool = os.getenv("DEBUG", "false").lower() not in ['false', '0']


# print('class stuff: ' + str(ENV.__dict__))
