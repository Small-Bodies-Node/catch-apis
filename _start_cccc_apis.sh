#! /bin/bash

eval $(cat .env | sed 's/^/export /')       ### Load vars defined in .env 

echo $PROCESS_NAME

gunicorn cccc_apis:app \
    --config gunicorn.config.py \
    --pid .pid.txt \
    --daemon \
    --name $PROCESS_NAME --bind '127.0.0.1:5001'



