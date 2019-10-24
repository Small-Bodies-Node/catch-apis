#!/usr/bin/env python

import requests
from sseclient import SSEClient

url = 'http://127.0.0.1:5002/catch-dev/query/moving?target=65P&cached=false'
res = requests.get(url)
data = res.json()
print(data)

messages = SSEClient('http://127.0.0.1:5002/catch-dev/stream')
for msg in messages:
    if msg.data == data['job_id']:
        break
print('task completed')

res = requests.get(data['results'])
data = res.json()
print(data)
