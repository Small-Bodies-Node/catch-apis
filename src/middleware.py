from data_provider_service import DataProviderService
import os
from flask import jsonify
# from flask import abort
# from flask import make_response
# from flask import request
# from flask import url_for

from typing import Optional
# Import .env vars and build URI
from dotenv import load_dotenv
load_dotenv(verbose=True)

DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME")
DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
DB_HOST: Optional[str] = os.getenv("DB_HOST")
DB_DATABASE: Optional[str] = os.getenv("DB_DATABASE")
# db_engine_URI: str = "mysql+pymysql://"+DB_USERNAME+":" + \
#     DB_PASSWORD + "@" + DB_HOST + "/" + DB_DATABASE

db_engine_URI: str = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"


DATA_PROVIDER = DataProviderService(db_engine_URI)


def ztf_data(serialize=True):
    '>>> ztf_data handler'
    print("===============")
    print("Running Candidate")
    print("===============")
    ztf_data = DATA_PROVIDER.get_ztf_data(serialize=serialize)
    if serialize:
        return jsonify({"candidates": ztf_data, "total": len(ztf_data)})
    else:
        return ztf_data


def moving_object_search(objid: str, start: int, end: int) -> str:
    '>>> moving_object_search handler'
    print("====================")
    print("MOVING OBJECT SEARCH")
    print("====================")
    mos_data = DATA_PROVIDER.get_moving_object_search_data(objid, start, end)
    print('^^^^^^^^^')

    d, a = {}, []
    for rowproxy in mos_data:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for tup in rowproxy.items():
            # build up the dictionary
            d = {**d, **{tup[0]: tup[1]}}
        a.append(d)
    print(a)
    return jsonify(mos_data)


def dosthmsk():
    '''
        <This is where you insert a call to your scripts>
    '''

    return jsonify({"message": "Hey! MSK just ran a script!!!"})
