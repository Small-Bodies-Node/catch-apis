"""SSOT FOR ENV VARIABLES"""

import os
from enum import Enum, auto
from typing import Optional
from dotenv import load_dotenv
load_dotenv(verbose=True)


# Match DEPLOYMENT_ENV string in .env to equivalent ENUM
class EDeploymentEnvironment(Enum):
    """ Enum possible values of deployment environment """
    PROD = auto()
    STAGE = auto()
    DEV = auto()


raw_deployment_env: Optional[str] = os.getenv("DEPLOYMENT_ENV")
APP_DEPLOYMENT_ENV: EDeploymentEnvironment = EDeploymentEnvironment.DEV
if raw_deployment_env == "STAGE":
    APP_DEPLOYMENT_ENV = EDeploymentEnvironment.STAGE
if raw_deployment_env == "PROD":
    APP_DEPLOYMENT_ENV = EDeploymentEnvironment.PROD


class ENV():
    """ Class to store all env variables used in app """

    # String properties
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_DIALECT: Optional[str] = os.getenv("DB_DIALECT")
    DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_DATABASE: Optional[str] = os.getenv("DB_DATABASE")
    DASHBOARD_CONFIG: Optional[str] = os.getenv("DASHBOARD_CONFIG")
    CATCH_FULLFRAME_BASE_URL: str = os.getenv('CATCH_FULLFRAME_BASE_URL',
                                              default='')
    CATCH_CUTOUT_BASE_URL: str = os.getenv('CATCH_CUTOUT_BASE_URL', default='')
    CATCH_ARCHIVE_PATH: str = os.getenv('CATCH_ARCHIVE_PATH', default='')
    CATCH_CUTOUT_PATH: str = os.getenv('CATCH_CUTOUT_PATH', default='')
    CATCH_LOG: str = os.getenv('CATCH_LOG', default='/dev/null')

    # Numeric properties
    REDIS_PORT: int = int(os.getenv("REDIS_PORT") or -1)
    PROD_GUNICORN_INSTANCES: int = int(os.getenv(
        "PROD_GUNICORN_INSTANCES") or -1)

    # Boolean properties; requires casting a string to bool
    DEVELOPMENT_MODE: bool = os.getenv("DEVELOPMENT_MODE") != 'False'

    # ENUM Properties
    DEPLOYMENT_ENV: EDeploymentEnvironment = APP_DEPLOYMENT_ENV


# print(ENV.PROD_GUNICORN_INSTANCES)
# print(ENV.DEVELOPMENT_MODE)
