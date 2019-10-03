"""
    Service class for querying SQL-DB
"""

import typing
from contextlib import contextmanager
import sqlalchemy
from sqlalchemy.orm.session import Session
from env import ENV

# Build URI and instantiate data-provider service
db_engine_URI: str = \
    f"{ENV.DB_DIALECT}://{ENV.DB_USERNAME}:{ENV.DB_PASSWORD}@{ENV.DB_HOST}/{ENV.DB_DATABASE}"
db_engine: typing.Any = sqlalchemy.create_engine(
    db_engine_URI, pool_recycle=3600)
db_session: typing.Any = sqlalchemy.orm.sessionmaker(bind=db_engine)


@contextmanager
def DATA_PROVIDER_SESSION() -> typing.Any:
    """Provide a transactional scope around a series of operations."""
    session: Session = db_session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
