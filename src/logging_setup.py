"""
Initialize logging configuration for app.
This script exists so that this content can be imported into app_entry
before importing restplus configurations
"""
import os
import logging
import logging.config

# Setup logging throughout application
logging_conf_path: str = os.path.normpath(os.path.join(
    os.path.dirname(__file__), '..', 'logging.ini'))
logging.config.fileConfig(logging_conf_path, disable_existing_loggers=False)
logger: logging.Logger = logging.getLogger(__name__)
