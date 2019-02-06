# CATCH APIS

## Conventions

Scripts for working with this code base begin '\_'

## OPERATING INSTRUCTIONS

1. Run `source _initial_setup.sh` in order to:

    1. Create a virtual environment 'venv' if it doesnt already exist
    2. Activate venv
    3. Install project dependencies

2. Run `sh _dev_cccc_apis.sh` to start the flask apis locally in development mode. [Nodemon](https://www.npmjs.com/package/nodemon) is used here to watch for file changes. (You'll need to install node and nodemon; if you prefer then you can just call `python cccc_apis.py` directly and restart whenever you make changes in development.)

3. Run `sh _start_cccc_apis.sh` to start the apis in production using gunicorn-worker processes in the background.

## GIT COMMITS

...

## TODOs

[] Add testing
[] Set up CI
[] Swagger docs

## DEVELOPMENT NOTES

-- DWD: I tried using conda virtual environments, but my local version of conda (4.6.2) seem to have breaking changes from remote conda (4.3.30), such as the way in which you `source activate` (the newer version replaces the script `activate` with the command `conda activate`). This made it tricky to coordiante the setup pipeline. Also, using `virtualenv` seemed overall to be simpler in the end.

-- DWD: I tried pip-installing a package `setproctitle` remotely, but it failed (probably because remote doesnt have python-dev package installed). If we get more trouble with installing packages with binary dependencies, etc. then we'll to switch over to conda environments.
