"""
This 'services' module defines singleton instances of classes designed
to get data and (ultimately) provide it to controllers.append()

For this app, the key providers will be (1) a mysql-db service
"""

from typing import Optional
import os
from dotenv import load_dotenv

# Import Services Classes
from .database_provider import DatabaseProvider

# 1.
# Load .env
load_dotenv(verbose=True)

# Initialize DataProvider's DB Connection
DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME")
DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
DB_HOST: Optional[str] = os.getenv("DB_HOST")
DB_DATABASE: Optional[str] = os.getenv("DB_DATABASE")

# Build URI and instantiate data-provider service
db_engine_URI: str = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"
DATA_PROVIDER = DatabaseProvider(db_engine_URI)

print("IMPORTING FROM SERVICES __INIT__")

# Export Initialized DataProvider Instance:
__all__ = ["DATA_PROVIDER"]
