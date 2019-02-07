from dataProviderService import DataProviderService
import os
from flask import jsonify
from flask import abort
from flask import make_response
from flask import request
from flask import url_for

# Import .env vars and build URI
from dotenv import load_dotenv
load_dotenv(verbose=True)

DB_USERNAME = os.getenv("DB_USERNAME")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_DATABASE = os.getenv("DB_DATABASE")
db_engine_URI = 'mysql+pymysql://'+DB_USERNAME+':' + \
    DB_PASSWORD+'@'+DB_HOST+'/'+DB_DATABASE

DATA_PROVIDER = DataProviderService(db_engine_URI)


def ztf_data(serialize=True):
    print("===============")
    print("Running Candidate")
    print("===============")
    ztf_data = DATA_PROVIDER.get_ztf_data(serialize=serialize)
    if serialize:
        return jsonify({"candidates": ztf_data, "total": len(ztf_data)})
    else:
        return ztf_data


def dosthmsk():
    '''
        <This is where you insert a call to your scripts>
    '''

    return jsonify({"message": "Hey! MSK just ran a script!!!"})
