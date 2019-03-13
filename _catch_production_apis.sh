#!/bin/sh

# ============================================================================
# This script is used to start/stop/restart the CATCH APIs in production mode
# ============================================================================


# Load vars defined in .env
eval $(cat .env | sed 's/^/export /')

# Test if we've already got gunicorn running from this project:
NUMBER_LAUNCHES=$(ps -ef |grep $PWD"/.venv\/bin\/gunicorn" | wc -l)

d_status() {

    if [[ $NUMBER_LAUNCHES -gt 0 ]]; then
        echo "Gunicorn is running with "$NUMBER_LAUNCHES" workers."
    else
        echo "No gunicorn process is running from this project's virtual environment at the moment."
    fi
}

d_start() {

    if [[ $NUMBER_LAUNCHES -gt 0 ]]; then
        echo "This API is already running in production; cancelling start!"
    else
        ### Enter src, start gunicorn, exit
        echo "--------------"
        echo "This API is not running; begin workers in production!"
        cd src
        echo $PWD
        ### Set running mode to production and start gunicorn
        gunicorn app_entry:flask_app \
            --config ..\/gunicorn.config.py \
            --pid ..\/.pid.txt \
            --daemon \
            --name $PROCESS_NAME --bind '127.0.0.1:5001'
        cd ..
        echo "--------------"
    fi
}

d_stop() {
    if [ -e .pid.txt ]; then
        echo "Stopping gunicorn process; this may take ~10 seconds..."
        kill -9 $(cat .pid.txt)
        sleep 10
        rm .pid.txt
        if [ -e .pid-old.txt ]; then
            rm .pid-old.txt
        fi
        echo "... done!"
    else
        #TODO: improve logic here:
        echo "No file '.pid.txt' found. Will not attempt to stop. Are you sure the API is running?"
    fi
}

d_restart() {
    if [ -e $PIDFILE ]; then
        cp .pid.txt .pid-old.txt
        # Reexec a new master with new workers
        kill -s USR2 `cat .pid.txt`
        # Graceful stop old workers
        kill -s WINCH `cat .pid-old.txt`
        # Graceful stop old master
        kill -s QUIT `cat .pid-old.txt`
        # sleep 10
    else
        echo "No file '.pid.txt' found! Try starting the API:"
        if [[ $NUMBER_LAUNCHES -gt 0 ]]; then
            echo "This API is already running in production; cancelling start!"
            echo "Something is messed up here; need to send notification to web master!"
        else
            ### Enter src, start gunicorn, exit
            cd src
            echo $PWD
            ### Set running mode to production and start gunicorn
            gunicorn app_entry:flask_app \
                --config ..\/gunicorn.config.py \
                --pid ..\/.pid.txt \
                --daemon \
                --name $PROCESS_NAME --bind '127.0.0.1:5001'
            cd ..
            echo "--------------"
        fi
    fi
}

case $1 in
    status)
    d_status
    ;;
    start)
    d_start
    ;;
    stop)
    d_stop
    ;;
    restart)
    d_restart
    ;;
    *)
    echo "usage: $NAME {status|start|stop|restart}"
    exit 1
    ;;
esac

exit 0