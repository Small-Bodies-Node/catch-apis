from typing import Optional, Any
import os
from flask import jsonify
from flask.wrappers import Response
from dotenv import load_dotenv

from data_provider_service import DataProviderService

### LOAD .ENV
load_dotenv(verbose=True)
DB_USERNAME: Optional[str] = os.getenv("DB_USERNAME")
DB_PASSWORD: Optional[str] = os.getenv("DB_PASSWORD")
DB_HOST: Optional[str] = os.getenv("DB_HOST")
DB_DATABASE: Optional[str] = os.getenv("DB_DATABASE")

# Build URI and instantiate data-provider service
db_engine_URI: str = f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB_DATABASE}"
DATA_PROVIDER = DataProviderService(db_engine_URI)


def ztf_data(serialize: bool = True) -> Any:
    ">>> ztf_data handler"
    returned_ztf_data = DATA_PROVIDER.get_ztf_data(serialize=serialize)
    if serialize:
        return jsonify({"data": returned_ztf_data, "total": len(returned_ztf_data)})
    return returned_ztf_data


def moving_object_search(objid: str, start: int, end: int) -> Response:
    '>>> moving_object_search handler'
    print("====================")
    print("MOVING OBJECT SEARCH")
    print("====================")
    mos_data = DATA_PROVIDER.get_moving_object_search_data(objid, start, end)
    # print(type(mos_data))
    print('^^^^^^^^^')

    # d: Any = {}
    # a: Any = []
    # for rowproxy in mos_data:
    #     # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
    #     for tup in rowproxy.items():
    #         # build up the dictionary
    #         d = {**d, **{tup[0]: tup[1]}}
    #     a.append(d)
    # print("a >>>")
    # print(a)
    # print("----------")
    # print("d >>>")
    # print(d)
    # print("----------")

    # return jsonify(mos_data)
    return jsonify({"data": mos_data, "total": len(mos_data)})


def doSthMsk() -> Any:
    '''
        <This is where you insert a call to your scripts>
    '''

    return jsonify({"message": "Hey! MSK just ran a script!!!"})
