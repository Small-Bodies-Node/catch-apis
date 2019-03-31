'''Service class for querying SQL-DB'''

import typing
import os
import sqlalchemy
from sqlalchemy.orm.session import Session
from dotenv import load_dotenv

# Load .env variables
load_dotenv(verbose=True)

# Initialize DataProvider's DB Connection
DB_USERNAME: typing.Optional[str] = os.getenv("DB_USERNAME")
DB_PASSWORD: typing.Optional[str] = os.getenv("DB_PASSWORD")
DB_HOST: typing.Optional[str] = os.getenv("DB_HOST")
DB_DATABASE: typing.Optional[str] = os.getenv("DB_DATABASE")

# Build URI and instantiate data-provider service
db_engine_URI: str = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"
db_engine: typing.Any = sqlalchemy.create_engine(db_engine_URI)
db_session: typing.Any = sqlalchemy.orm.sessionmaker(bind=db_engine)
DATA_PROVIDER_SESSION: Session = db_session()
