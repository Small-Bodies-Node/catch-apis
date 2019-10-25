# CATCH API

## OPERATING INSTRUCTIONS

### OVERVIEW

- This is a flask webapp
- It uses a python virtual environment launched by running `source _init_setup`
- The library `FlaskRestPlus` is used to generate swagger documentation
- The app uses redis and the python `rq` library to perform long-lived/async tasks
- Environment variables are set in `.env` that you create by copying and editing the `.env-template` file
- To launch the app in production, you need to have running:
  - the flask application server itself with gunicorn launched with `_gunicorn_manager`
  - A `redis-server` instance; the script `_redis_manager` will let you install/start/stop/restart a redis instance
  - workers to process the queued tasks launched with `_workers_manager`; this script uses pm2 under the hood, so you need to have node installed with a global `pm2` package
  - a web server to proxy-pass http requests to the gunicorn workers; we use apache
  - postgres DB

### LOCAL DEVELOPMENT

To develop this flask API locally on a linux-like machine:

1. Environment Variables

   1. Copy `.env-template` to `.env` and supply labels/credentials.
   2. You'll need to specify a python interpreter of version 3.5 or higher to `PYTHON_3_5_OR_HIGHER`.
   3. Ask an admin for DB credentials.
   4. The `PYTHONPATH` variable is needed iff you're using vscode (to enable the microsoft python server to resolve modules).
   5. `DASHBOARD_CONFIG` needs to point to a file called `.config.cfg` in your root directory; create one by copying from `.config-template.cfg` and setting variables therein accordingly.
   6. Create an empty file `.dashboard.db` in your root directory; this will be used by the flask_monitoringdashboard library to track API usage
   7. `TEST_URL_BASE` is used in the script `_demo_routes`; you're unlikely to need to change this.
   8. `CATCH_ARCHIVE_PATH` is the source directory for local data.
   9. `CATCH_CUTOUT_PATH` and `CATCH_THUMBNAIL_PATH` are the directories to which cutouts and thumbnails are saved.
   11. `CATCH_ARCHIVE_BASE_URL`, `CATCH_CUTOUT_BASE_URL`, and `CATCH_THUMBNAIL_BASE_URL` are the URL prefixes for serving the archive, cutouts, and thumbnails.

2. Run `source _initial_setup` in order to:

   1. Create a virtual environment '.venv' if it doesn't already exist
   2. Activate .venv
   3. Update pip
   4. Install project dependencies
   5. Install npm packages
   6. Checks for files and other misc steps

   Note: `source _initial_setup` is an idempotent process of readying your dev environment, so you can call it liberally.

3. Run `_start_dev_api` to start the flask api directly in development mode. [Nodemon](https://www.npmjs.com/package/nodemon) is used here to watch for file changes as you develop. (You'll thus need to have node and nodemon installed; if you prefer then you can just call `python3 -m src/app_entry.py` directly and restart it whenever you make changes in development.)

4. If in the course of your development you add new package dependencies, don't forget to 'freeze' your changes by running `_freeze_requirements` while in the `.venv`, and commit those changes.

5. To test the routes, there is a crude `_test_routes` script that prints out the result of making local http requests to the defined routes. This will be augmented/replaced with proper end-to-end tests soon.

6. Go to `localhost:5001/catch/docs` to see the swagger documentation for the API

### RUNNING IN PRODUCTION

The production version of the API uses gunicorn to start the workers that serve content according to the python-flask configurations. This is controlled by the script `_catch_production_apis`, with one of the following arguments: `start, stop, restart, status`.

### GIT WORKFLOW

- Commit often with super clear messages
- Make sure that your master branch is synced with your local master branch
- Use `git fetch` to update your local tracking copy of the remote master branch (locally called `origin/master`) and merge it into your local master using `git merge origin/master`
- Always create feature branches from your freshly updated master branch; commit your changes frequently, and push them to make sure work isn't lost. I usually just use `git push origin HEAD` when working on a feature branch
- When you're ready to merge your branch, go to github and create a pull request for your new branch; this will trigger tests on Jenkins; if these pass then you'll be able to merge those changes; when a merge is activated on github it will trigger an update to the codebase on the production server and will automatically restart gunicorn without downtime

## CODEBASE CONVENTIONS

The following tools/conventions are used to promote codebase quality amidst multiple developers

### File Naming

- Scripts for working with this code base always begin '\_'.
- All application source code is placed in the `src` dir
- Configuration files are to be saved in the root dir
- Ad-hoc instruction files are to be labelled README.md, and can be placed in any dir

### Tooling

- mypy (with vscode integration)

  - Please add python typings to ALL aspects of the code base (all classes, functions, etc.)
  - mypy is configured in the `mypy.ini` file. The settings are quite strict at the moment.

- autopep8

  - When you initialize your virtual environment, a git pre-commit hook is established. This causes `_precommit_hook` to be run before the commit is made. The main purpose of this is to run `autopep8` auto-formatting on all python files.
  - I highly recommend that you configure your code editor so that it automatically formats your code on save. Template VSCode settings are provided.

- pylint

  - To check your code quality, run `sh _pylint_code`. This will generate a report on the neatness/quality of your code.
  - I highly recommnd you configure your code editor to flag code-format problems according to pylint analysis. Template VSCode settings are provided.
  - pylint configuration details are given in .pylint

- pytest
  - Unit-test capabilities are in place; just run `sh _run_tests` to execute them. Failed tests will cause merge requests to be rejected if attempted at origin. Tests are recommended mainly for functions that you expect to be established for the long haul.

## TODOs

## DEVELOPMENT NOTES

These are misc notes where you can describe issues/decisions-taken in the course of development (especially if the motivation for sth may not be clear, etc.)

-- DWD: I tried using conda virtual environments, but my local version of conda (4.6.2) seem to have breaking changes from remote conda (4.3.30), such as the way in which you `source activate` (the newer version replaces the script `activate` with the command `conda activate`). This made it tricky to coordinate the setup pipeline. Also, using `virtualenv` seemed overall to be simpler in the end.

-- DWD: Introducing python typings into the mix broke remote since it's only supported by python >=3.5. I tried switching to the anaconda executable, but this proved incompatible with the pre-installed virtualenv. I therefore created a conda venv and installed therein (i) the latest version of python (3.7.2), and (ii) a conda-compatible virtualenv. These now have to be specified in `.env`.

-- DWD: I tried pip-installing a package `setproctitle` remotely, but it failed (probably because remote doesn't have python-dev package installed). If we get more trouble with installing packages with binary dependencies, etc. then we'll to switch over to conda environments.

-- DWD: Added `sqlalchemy-stubs` to make `mypy` comply better with models generated by `sqlacodegen`. This caused type errors to arise with the `Column` function imported from `sqlalchemy`, but I expect this will get solved at some point (since `sqlalchemy-stubs` are in early development).

-- DWD: When it came to adding swagger documentation, the main contenders (based on python entries in [this list](https://swagger.io/tools/open-source/open-source-integrations/)) seemed to be `flask_restplus`, `flassger` and `connexion`. I've gone with `flask_restplus` first.

-- DWD: NOTE: regretfully, the decision to go with `flask_restplus` may have been a bad one since the project [seems to have been abandoned](https://github.com/noirbizarre/flask-restplus/issues/593) by its original creator :(

-- DWD: NOTE: this codebase has '/' file separators hard-coded, e.g. in logging.ini files; that, plus the bash scripts, makes this codebase inhospitable to windows machines.

-- DWD: NOTE: the script `_initial_setup` must be sourced (not sh-ed) because it exports env variables. To try to prevent sh-ing I used a 'trick' taken from [here](https://stackoverflow.com/a/47613477/8620332) to test if the script was sourced. That seemed to work but, beware, it causes Jenkins' builds to fail, so I added some optional logic to by-pass that test; just be sure to use 'source' in your Jenkins builds!

-- DWD: NOTE: there seems to be a weird edge case when using flask_restplus namescpaces whereby the description string will truncate repeated '!' symbols to a maximum of 3. This is really odd; I can't imagine why `flask_restplus` would want to do any string formatting on the description, let alone something as niche as ensuring that !!!... is limited to three chars max.

-- DWD: CORS proved tricky with `flask_restplus`; haven't been able to find a way to make all routes CORS-able; basic means of CORS-ing routes have been added to `demo_routes.py`. For routes that use [flask_restplus response marshalling](https://flask-restplus.readthedocs.io/en/stable/marshalling.html), the only way I've found is to set the header in the controller's return statement (viz. see `moving_object_search.py`).

-- DWD: Started getting error from API: "An unhandled exception occurred. Error Message: (sqlalchemy.exc.InvalidRequestError) Can't reconnect until invalid transaction is rolled back". According to this [article](https://mofanim.wordpress.com/2013/01/02/sqlalchemy-mysql-has-gone-away/), it probably has to do with session timeouts perhaps associated with the app's low traffic while in development.

-- DWD: implemented some simple plotly templates, but this was causing VSCode to overheat and I've decided to focus on doing all plotting visualizations in the frontend, so I've now now removed all vestiges

-- DWD: to get redis working, you need to choose a stable release from [https://redis.io/download](https://redis.io/download), and insert it into `.env`. As of Sept 2019, this is `REDIS_DIST='redis-5.0.5'`. The `_init_setup` script will then install it locally if it doesn't exist. The script `_redis_server` will then provide you with `install/start/stop/restart/status` options.

-- DWD: to start gunicorn from the project root acting on an app within the `src` directory, you either need to cd in/out of `src` in your `_gunicorn_manager` script or apply the flag `--chdir src` when calling gunicorn. I discovered however that the latter option messed up my restart mechanism (where I send a series of signals with the `kill` command). Not wanting to figure out what the issuse was there, I reverted to cd in/out.
