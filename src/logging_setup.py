"""
    Initialize logging configuration for app.
    This script exists so that this content can be imported into app_entry
    before importing restplus configurations
"""

import os
import logging
import logging.config
from env import ENV

print("++++++++++++++")
print(ENV.DEPLOYMENT_TIER)

# Setup logging throughout application
logging_config_name: str = "logging_prod.ini" \
    if ENV.IS_DAEMON else "logging_dev.ini"

logging_conf_path: str = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..', 'logging', logging_config_name))

logging.config.fileConfig(logging_conf_path, disable_existing_loggers=False)

logger: logging.Logger = logging.getLogger(__name__)
