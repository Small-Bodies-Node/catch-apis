from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from models import Ztf


class DataProviderService:

    # Init engine
    def __init__(self, engine):
        if not engine:
            raise ValueError(
                'The values specified in engine parameter has to be supported by SQLAlchemy')
        self.engine = engine
        db_engine = create_engine(engine)
        db_session = sessionmaker(bind=db_engine)
        self.session = db_session()

    def get_ztf_data(self, serialize=False):

        all_ztf_data = []

        all_ztf_data = self.session.query(
            Ztf).order_by(Ztf.obsid).limit(50)

        # Ztf.

        if serialize:
            return [cand.serialize() for cand in all_ztf_data]
        else:
            return all_ztf_data
