"""
STAGE 0 of Pipeline
Perform memoized downloading of raw data files from online sources
"""

import re
import os
import subprocess as sub
from time import sleep
from typing import List
from bs4 import BeautifulSoup, element
from requests import Response, request
from models.name_search import NameSearch

###############################
# Setup data dir and file paths
###############################

# Compute dirname of this file
dirname: str = os.path.dirname(os.path.realpath(__file__))

# Define path to data dir
dataDirPath = dirname + '/mpcdata'

# Test data dir exists called 'mpcdata'
isDataDir: bool = os.path.isdir(dataDirPath)

# If data dir does not exist, create it
if not isDataDir:
    print("Data directory %s does not exist. Creating ..." % dataDirPath)
    sleep(1)
    try:
        os.mkdir(dataDirPath)
    except OSError:
        print("Creation of the directory %s failed" % dataDirPath)
    else:
        print("Successfully created the directory %s " % dataDirPath)

# Compute path to raw-html file
comet_html_file: str = dataDirPath + '/raw_mpc.html'

# Path to downloaded json file
asteroid_json_file = dataDirPath + '/cometels.json'

# Path to csv file to be created in next stage
name_search_items_csv_file: str = dataDirPath + "/minor_planets_names.csv"


############################
# Download remote data files
############################

if __name__ == '__main__':

    CMD = f"""

        ### get zipped asteroid data
        curl https://www.minorplanetcenter.net/Extended_Files/cometels.json.gz -o {asteroid_json_file}.gz;
        gunzip {asteroid_json_file}.gz

        ### get html comet data
        curl https://www.minorplanetcenter.net/iau/lists/MPNames.html -o {comet_html_file};

    """

    # print(CMD)
    # print(sub.PIPE)
    # print(sub.STDOUT)
    sub.Popen(CMD, shell=True, stdout=sub.PIPE, stderr=sub.STDOUT)
