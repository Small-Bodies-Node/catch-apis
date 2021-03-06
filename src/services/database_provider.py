"""
    Service class for querying SQL-DB
"""

from typing import Iterator
from contextlib import contextmanager

import sqlalchemy
from sqlalchemy.engine import Engine
from sqlalchemy.orm.session import Session, sessionmaker
from sqlalchemy.orm import scoped_session
from sqlalchemy.exc import SQLAlchemyError, DBAPIError
from sqlalchemy.pool import NullPool

from catch import Catch, Config
from env import ENV

# Build URI and instantiate data-provider service
db_engine_URI: str = (
    f"{ENV.DB_DIALECT}://{ENV.DB_USERNAME}:{ENV.DB_PASSWORD}@{ENV.DB_HOST}"
    f"/{ENV.DB_DATABASE}")
db_engine: Engine = sqlalchemy.create_engine(
    db_engine_URI, poolclass=NullPool, pool_recycle=3600, pool_pre_ping=True)
db_session: scoped_session = scoped_session(sessionmaker(bind=db_engine))

# catch library configuration
catch_config: Config = Config(log=ENV.CATCH_LOG)


@contextmanager
def data_provider_session() -> Iterator[Session]:
    """Provide a transactional scope around a series of operations."""
    session: Session = db_session()
    try:
        yield session
        session.commit()
    except (SQLAlchemyError, DBAPIError):
        session.rollback()
        raise
    finally:
        db_session.remove()


@contextmanager
def catch_manager(save_log: bool = True) -> Iterator[Catch]:
    """Catch library session manager."""
    with Catch(catch_config, session=db_session(), save_log=save_log) as catch:
        yield catch
