# CATCH APIS

## OPERATING INSTRUCTIONS

1. Run `source _initial_setup.sh` in order to:

    1. Create a virtual environment 'venv' if it doesnt already exist
    2. Activate venv
    3. Install project dependencies

2. Run `_dev_cccc_apis.sh` to start the flask apis locally in development mode. [Nodemon](https://www.npmjs.com/package/nodemon) is used here to watch for file changes. (You'll need to install node and nodemon; if you prefer then you can just call `python cccc_apis.py` directly and restart whenever you make changes in development.)

3. Run `_start_cccc_apis.sh` to start the apis in production using gunicorn-worker processes in the background.

## GIT COMMITS

...
