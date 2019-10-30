"""SSOT FOR ENV VARIABLES"""

import os
from enum import Enum, auto
from typing import Optional
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True, verbose=True)


class EDeploymentTier(Enum):
    """ Enum possible values of deployment tier """
    LOCAL = auto()
    SANDBOX = auto()
    STAGE = auto()
    PROD = auto()


raw_deployment_tier: Optional[str] = os.getenv("DEPLOYMENT_TIER")
APP_DEPLOYMENT_TIER: EDeploymentTier = EDeploymentTier.LOCAL
if raw_deployment_tier == "SANDBOX":
    APP_DEPLOYMENT_TIER = EDeploymentTier.SANDBOX
if raw_deployment_tier == "STAGE":
    APP_DEPLOYMENT_TIER = EDeploymentTier.STAGE
if raw_deployment_tier == "PROD":
    APP_DEPLOYMENT_TIER = EDeploymentTier.PROD


class ENV():
    """ Class to store all env variables used in app """

    # String properties
    DB_HOST: Optional[str] = os.getenv("DB_HOST")
    DB_DIALECT: Optional[str] = os.getenv("DB_DIALECT")
    DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME")
    DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
    DB_DATABASE: Optional[str] = os.getenv("DB_DATABASE")
    DASHBOARD_CONFIG: Optional[str] = os.getenv("DASHBOARD_CONFIG")
    CATCH_ARCHIVE_BASE_URL: str = os.getenv('CATCH_ARCHIVE_BASE_URL',
                                            default='')
    CATCH_CUTOUT_BASE_URL: str = os.getenv('CATCH_CUTOUT_BASE_URL', default='')
    CATCH_THUMBNAIL_BASE_URL: str = os.getenv(
        'CATCH_THUMBNAIL_BASE_URL', default='')
    CATCH_ARCHIVE_PATH: str = os.getenv('CATCH_ARCHIVE_PATH', default='')
    CATCH_CUTOUT_PATH: str = os.getenv('CATCH_CUTOUT_PATH', default='')
    CATCH_THUMBNAIL_PATH: str = os.getenv('CATCH_THUMBNAIL_PATH', default='')
    CATCH_LOG: str = os.getenv('CATCH_LOG', default='/dev/null')

    # Numeric properties
    REDIS_PORT: int = int(os.getenv("REDIS_PORT") or -1)
    PROD_GUNICORN_INSTANCES: int = int(os.getenv(
        "PROD_GUNICORN_INSTANCES") or -1)

    # ENUM Properties
    DEPLOYMENT_TIER: EDeploymentTier = APP_DEPLOYMENT_TIER

    # Boolean Properties
    IS_DAEMON: bool = os.getenv("IS_DAEMON") == 'TRUE'


# Debugging block
# print("=========================")
# print(ENV.PROD_GUNICORN_INSTANCES)
# print(ENV.DEPLOYMENT_TIER)
# print(ENV.DB_DATABASE)
# print(ENV.DB_PASSWORD)
# print(ENV.DB_USERNAME)
# print()
# print(ENV.CATCH_LOG)
# print(ENV.CATCH_ARCHIVE_PATH)
# print(ENV.CATCH_CUTOUT_PATH)
# print(ENV.CATCH_THUMBNAIL_PATH)
# print("=========================")
