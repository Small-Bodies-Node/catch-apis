# CATCH API

## OPERATING INSTRUCTIONS

### LOCAL DEVELOPMENT

To develop this flask API locally on a linux-like machine:

1. Copy `.env-template` to `.env` and supply labels/credentials. You'll need to specify a `python version` and a `virtualenv`. (If you're using anaconda then you'll probably have to use the version of virtualenv that you can install using the conda package manager).

2. Run `source _initial_setup.sh` in order to:

    1. Create a virtual environment '.venv' if it doesn't already exist
    2. Activate .venv
    3. Update pip
    4. Install project dependencies

3. Run `sh _start_dev_api.sh` to start the flask api directly in development mode. [Nodemon](https://www.npmjs.com/package/nodemon) is used here to watch for file changes as you develop. (You'll thus need to have node and nodemon installed; if you prefer then you can just call `python3 -m src/app_entry.py` directly and restart it whenever you make changes in development.)

4. If in the course of your development you add new package dependencies, don't forget to 'freeze' your changes by running `sh _freeze_requirements.sh` while in the `.venv`, and commit those changes.

5. To test the routes, there is a crude `_test_routes.sh` script that prints out the result of making local http requests to the defined routes. This will be augmented/replaced with proper end-to-end tests soon.

6. Go to `localhost:5001/catch/docs` to see the swagger documentation for the API

### RUNNING IN PRODUCTION

The production version of the API uses gunicorn to start the workers that serve content according to the python-flask configurations. This is controlled by the script `_catch_production_apis.sh`, which one of the following arguments: `start, stop, restart, status`.

### GIT WORKFLOW

-   Commit often with super clear messages
-   Make sure that your master branch is synced with your local master branch
-   Use `git fetch` to update your local tracking copy of the remote master branch (locally called `origin/master`) and merge it into your local master using `git merge origin/master`
-   Always create feature branches from your freshly updated master branch; commit your changes frequently, and push them to make sure work isn't lost. I usually just use `git push origin HEAD` when working on a feature branch
-   When you're ready to merge your branch, go to github and create a pull request for your new branch; this will trigger tests on Jenkins; if these pass then you'll be able to merge those changes; when a merge is activated on github it will trigger an update to the codebase on the production server and will automatically restart gunicorn without downtime

## CODEBASE CONVENTIONS

The following tools/conventions are used to promote codebase quality amidst multiple developers

### File Naming

-   Scripts for working with this code base always begin '\_'.
-   All application source code is placed in the `src` dir
-   Configuration files are to be saved in the root dir
-   Ad-hoc instruction files are to be labelled README.md, and can be placed in any dir

### Tooling

-   mypy (with vscode integration)
    -   Please add python typings to ALL aspects of the code base (all classes, functions, etc.)

## GENERATING SQLALCHEMY-ORM MODELS

This only needs to be done when the DB schema gets changed. Run `_generate_models.sh` to generate an output of the latest DB schema translated into sqlalchemy-ORM syntax in `generated-models/gen-models.txt`, then we essentially copy-paste those contents into `src/models.py`

## TODOs

[] Add BLACK auto-formatting with git hooks
[] Set up monitoring with e.g. `https://prometheus.io`
[] Set up development deployment

## DEVELOPMENT NOTES

These are misc notes where you can describe issues/decisions-taken in the course of development (especially if the motivation for sth may not be clear, etc.)

-- DWD: I tried using conda virtual environments, but my local version of conda (4.6.2) seem to have breaking changes from remote conda (4.3.30), such as the way in which you `source activate` (the newer version replaces the script `activate` with the command `conda activate`). This made it tricky to coordinate the setup pipeline. Also, using `virtualenv` seemed overall to be simpler in the end.

-- DWD: Introducing python typings into the mix broke remote since it's only supported by python >=3.5. I tried switching to the anaconda executable, but this proved incompatible with the pre-installed virtualenv. I therefore created a conda venv and installed therein (i) the latest version of python (3.7.2), and (ii) a conda-compatible virtualenv. These now have to be specified in `.env`.

-- DWD: I tried pip-installing a package `setproctitle` remotely, but it failed (probably because remote doesn't have python-dev package installed). If we get more trouble with installing packages with binary dependencies, etc. then we'll to switch over to conda environments.

-- DWD: Added `sqlalchemy-stubs` to make `mypy` comply better with models generated by `sqlacodegen`. This caused type errors to arise with the `Column` function imported from `sqlalchemy`, but I expect this will get solved at some point (since `sqlalchemy-stubs` are in early development).

-- DWD: When it came to adding swagger documentation, the main contenders (based on python entries in [this list](https://swagger.io/tools/open-source/open-source-integrations/)) seemed to be `flask_restplus`, `flassger` and `connexion`. I've gone with `flask_restplus` first.

-- DWD: NOTE: regretfully, the decision to go with `flask_restplus` may have been a bad one since the project [seems to have been abandoned](https://github.com/noirbizarre/flask-restplus/issues/593) by its original creator :(

-- DWD: NOTE: this codebase has '/' file separators hard-coded, e.g. in logging.ini files; that, plus the bash scripts, makes this codebase inhospitable to windows machines.

-- DWD: NOTE: the script `_initial_setup.sh` must be sourced (not sh-ed) because it exports env variables. To try to prevent sh-ing I used a 'trick' taken from [here](https://stackoverflow.com/a/47613477/8620332) to test if the script was sourced. That seemed to work but, beware, it causes Jenkins' builds to fail, so I added some optional logic to by-pass that test; just be sure to use 'source' in your Jenkins builds!

-- DWD: NOTE: there seems to be a weird edge case when using flask_restplus namescpaces whereby the description string will truncate repeated '!' symbols to a maximum of 3. This is really odd; I can't imagine why `flask_restplus` would want to do any string formatting on the description, let alone something as niche as ensuring that !!!... is limited to three chars max.

-- DWD: CORS proved tricky with `flask_restplus`; haven't been able to find a way to make all routes CORS-able; basic means of CORS-ing routes have been added to `demo_routes.py`. For routes that use [flask_restplus response marshalling](https://flask-restplus.readthedocs.io/en/stable/marshalling.html), the only way I've found is to set the header in the controller's return statement (viz. see `moving_object_search.py`).

-- DWD: Started getting error from API: "An unhandled exception occurred. Error Message: (sqlalchemy.exc.InvalidRequestError) Can't reconnect until invalid transaction is rolled back". According to this [article](https://mofanim.wordpress.com/2013/01/02/sqlalchemy-mysql-has-gone-away/), it probably has to do with session timeouts perhaps associated with the app's low traffic while in development.

-- DWD: implemented some simple plotly templates, but this was causing VSCode to overheat, so I've commented it out for now
