import os
import requests


def _test_ztf_labels() -> None:
    url = 'http://{}/ztf'.format(os.getenv('TEST_URL_BASE'))
    q = requests.get(url + '/found?objid=909').json()
    labels = requests.get(url + '/found/labels').json()

    for col in q['data'][0]:
        #assert col in labels
        pass
