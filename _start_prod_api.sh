#! /bin/bash

### Load vars defined in .env 
eval $(cat .env | sed 's/^/export /')       

### Enter src, start gunicorn, exit
cd src
gunicorn appEntry:app \
    --config ..\/gunicorn.config.py \
    --pid ..\/.pid.txt \
    --daemon \
    --name $PROCESS_NAME --bind '127.0.0.1:5001'
cd ..


