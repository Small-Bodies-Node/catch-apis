# CATCH API

## Conventions

Scripts for working with this code base begin '\_'

## OPERATING INSTRUCTIONS

To run/develop this flask API locally on a linux-like machine:

1. Copy `.env-template` to `.env` and supply labels/credentials. It's recommended that you choose a local installation of python3 (viz. `which -a python3`) that is not supplied by anaconda, as that might lead to issues.

2. Run `source _initial_setup.sh` in order to:

    1. Create a virtual environment 'venv' if it doesnt already exist
    2. Activate venv
    3. Install project dependencies

3. Run `sh _start_dev_api.sh` to start the flask api locally in development mode. [Nodemon](https://www.npmjs.com/package/nodemon) is used here to watch for file changes. (You'll need to install node and nodemon; if you prefer then you can just call `python src/app_entry.py` directly and restart whenever you make changes in development.)

4. Run `sh _start_prod_api.sh` to start the api in production mode using gunicorn-worker processes in the background.

## GENERATING MODELS

...

## GIT COMMITS

...

## TODOs

[] Add testing
[] Set up CI
[] Swagger docs

## DEVELOPMENT NOTES

-- DWD: I tried using conda virtual environments, but my local version of conda (4.6.2) seem to have breaking changes from remote conda (4.3.30), such as the way in which you `source activate` (the newer version replaces the script `activate` with the command `conda activate`). This made it tricky to coordiante the setup pipeline. Also, using `virtualenv` seemed overall to be simpler in the end.

-- DWD: I tried pip-installing a package `setproctitle` remotely, but it failed (probably because remote doesnt have python-dev package installed). If we get more trouble with installing packages with binary dependencies, etc. then we'll to switch over to conda environments.
