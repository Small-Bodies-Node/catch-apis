# CATCH-APIs v3.0

[![CI Tests](https://github.com/Small-Bodies-Node/catch-apis/actions/workflows/ci-tests.yml/badge.svg)](https://github.com/Small-Bodies-Node/catch-apis/actions/workflows/ci-tests.yml)

An API for the Planetary Data System Small Bodies Node survey data search tool:
catch comets and asteroids in wide-field sky survey data.

## Overview

CATCH-APIs provide a REST API service that enable a user to search for potential
observations of comets and asteroids in wide-field sky survey data. This API is
designed for use by the Planetary Data System Small Bodies Node (SBN) at the
University of Maryland, but it is possible to deploy anywhere with other data
sets. SBN is the primary archive for the Near-Earth Asteroid Tracking (NEAT)
survey, the Asteroid Terrestrial-impact Last Alert System (ATLAS), the Catalina
Sky Survey, and Spacewatch. CATCH-APIs is one of the primary methods for users
to discover scientifically interesting data in those data sets.

The API uses the following:

- The [catch](https://github.com/Small-Bodies-Node/catch) and
  [sbsearch](https://github.com/Small-Bodies-Node/sbsearch) Python libraries,
  which define how survey metadata is stored and execute the actual searches on
  the database.
  - The [s2geometry](http://s2geometry.io/) C++ library is used for spatial
    indexing on the Celestial Sphere.
  - Target ephemerides are generated by
    [Horizons](https://ssd.jpl.nasa.gov/horizons/) at NASA JPL via
    [astroquery](https://astroquery.readthedocs.io/).
  - [SQLAlchemy](https://www.sqlalchemy.org/) and
    [PostgreSQL](https://www.postgresql.org/) store user queries and survey
    metadata.
  - Metadata ingestion uses
    [pds4_tools](https://github.com/Small-Bodies-Node/pds4_tools).
- [flask](https://flask.palletsprojects.com/),
  [connexion](https://connexion.readthedocs.io/),
  [openapi](https://swagger.io/specification/), and
  [gunicorn](https://gunicorn.org/) for the API experience and documentation.
- [redis](https://redis.io/) for the job queue and user task messaging.
- [docker](https://www.docker.com/) is used for cross-platform development and deployment

## Features

- A single observation table holds all observations from all surveys. This
  feature allows for an approximate search that can ignore parallax and search
  all surveys in one go.  Fine for objects a few au a way or more.
- The S2 library cells range from 3 arcmin to 1 deg.
- Ephemerides may create loops on the sky (e.g., during retrograde motion), this
  is correctly handled by S2, even when padding the ephemeris with some
  uncertainty.
- Ephemerides are split segments, and the database is queried for each.  This
  improves performance because the points in each segment are spatially
  correlated.

## Data-Flow Overview

These APIs wrap the functionality given by the
[catch](https://github.com/Small-Bodies-Node/catch) and
[sbsearch](https://github.com/Small-Bodies-Node/sbsearch) libraries.

1. A user submits a query for a comet or asteroid, e.g. '65P', to the `/catch`
   route; e.g.
   `/catch?target=65P&sources=neat_palomar_tricam&uncertainty_ellipse=true&padding=0&cached=true`.
2. If the object has been found previously, and if the query option `'cached'`
   is set to true, then the response will indicate that you can immediately
   access the scientific data by passing the stated `'job_id'` to the
   `/caught/:job_id` route; e.g., the URL in the `'results'` field:

   ```json
   {
     "job_id": "6b9499cf8dd34e94a4e5bc26ccbf45de",
     "message": "Found cached data.  Retrieve from results URL.",
     "message_stream": "http://catch-v2.astro-prod-it.aws.umd.edu/stream",
     "query": {
       "cached": true,
       "padding": 0,
       "sources": ["neat_palomar_tricam"],
       "target": "65P",
       "uncertainty_ellipse": true
     },
     "queue_full": false,
     "queued": false,
     "results": "http://catch-v2.astro-prod-it.aws.umd.edu/caught/6b9499cf8dd34e94a4e5bc26ccbf45de",
     "version": "2.0.0"
   }
   ```

3. If the object has not been previously found, or had the user set `'cached'`
   to false, then a new job will be posted to the CATCH APIs queue (implemented
   with redis). The response to the user will have `queued = true`.
   1. A separate worker process will claim that job and execute the query with
      the underlying [catch](https://github.com/Small-Bodies-Node/catch) and
      [sbsearch](https://github.com/Small-Bodies-Node/sbsearch) libraries to
      generate the scientific data for that comet or asteroid.
   2. During this job, the worker will post status messages back to the redis
      queue. These messages are available to the user via the `/stream` route
      (see `'message_stream'` field in the above JSON response). See the second
      on the [user messaging stream](#user-messaging-stream) below for more
      details.
   3. Once complete, the worker will save the results to the database and
      publish a `"status": "success"` message to the message stream. Because
      this will take an unknown amount of time to complete, one can subscribe to
      the server-sent-event route at `/stream`, and monitor the status messages
      labeled with their job prefix.

Note: there are two types of "worker" to think about in this code base. There
are the gunicorn workers that handle the http requests within the "apis"
service, and there are the workers that accept tasks from the redis queue and
carry out the computationally expensive workload. We try wherever possible to
label this latter kind of redis-queue ('RQ') workers as "woRQer".

### User messaging stream

CATCH searches generally take more than a few seconds to complete. After a
search is enqueued, the user is notified of the progress via the `/stream`
route.

The `/stream` route implements messaging using server sent events ([SSE][1]).
The messages sent by CATCH APIs are JSON-formatted text, e.g.,:

```
data: {"job_prefix": "4ed052ff", "text": "Starting moving target query.", "status": "running"}
data: {"job_prefix": "4ed052ff", "text": "Query NEAT from 2001-11-20 to 2003-03-11.", "status": "running"}
data: {"job_prefix": "4ed052ff", "text": "Obtained ephemeris from JPL Horizons.", "status": "running"}
data: {"job_prefix": "4ed052ff", "text": "Caught 5 observations.", "status": "running"}
...
data: {"job_prefix": "4ed052ff", "text": "Task complete.", "status": "success"}
```

Each message is labeled with the first eight characters of the user's `job_id`
to prevent data piracy. A user would monitor the stream for their own messages
to track the status of their query via the `'status'` field, which can take the
values:

- `'queued'`: the query has been received and is waiting for a woRQer to execute
  it.
- `'running'`: a woRQer is executing the query.
- `'success'`: the query terminated without error.
- `'error'`: the query terminated with an error. In all cases, the `'text'`
  field explains the status in a human-readable format.

Internally, messages are passed from the woRQers to the main thread running the
`/stream` route with a redis stream using XADD/XREAD. The redis stream preserves
a limited message history so that a user's connection can be interrupted without
the status of the query being immediately lost.

[1]: https://html.spec.whatwg.org/multipage/server-sent-events.html#server-sent-events

## Development Setup

### Using Docker

CATCH-APIs may be developed and run using docker. To develop locally:

- Install `docker` and `docker-compose-v2` on your machine.
- Clone this repo.
- Copy .env-template to .env and edit.
- CATCH requires a Postgres database populated with survey image metadata. This
  data can be harvested from the original source files, or simply a copy of a
  prior database.
  - If starting from a blank database, see [Adding New Data](#adding-new-data).
  - If starting from a copy of a prior database, we recommend using a file
    generated by the `pg_dump` program. Please contact
    [MKelley](https://github.com/mkelley) or [D-W-D](https://github.com/d-w-d)
    for the data. Copy that file within your clone of this repo to
    `.pg-init-data/some-name.backup`.
- Run docker compose:
  - There are two ways to start all of the relevant containers: dev mode and
    prod mode. In development mode, the code base for the apis will be
    "bind-mounted" into the container so that changes made to the code on your
    machine get reflected instantly in the running application (the API and
    woRQer processes are run via nodemon in dev mode). In prod mode, the
    code-base is installed from github, so changes will not be picked up
    dynamically at run-time.
  - To run everything in development mode, run `docker compose -f docker-compose.dev.yml up --build`
  - To stop everything, enter CTRL+C once to stop processes gracefully;
    sometimes this might fail to properly shutdown everything, in which case you
    can swap `... up --build` with `... down` to re-try shutting everything down
    - Also, when you bring docker compose systems up/down, it's sometimes
      helpful to also remove the stopped containers with `docker container prune`
  - To run everything in prod mode, run `docker compose -f
docker-compose.prod.yml up --build`
- DB setup:
  - The CATCH tool requires a postgresDB populated with initial data. In
    previous implementations, this DB was provided as a separate docker
    container. Now, however, we have separated the DB into its own postgres
    service on AWS RDS. If you want to develop this code, you therefore need to
    connect to the development db on our group's AWS instance (contact DWD or
    MSK for access), or you need to set up your own postgres instance and
    populate with data.
- Once everything is running in dev mode, visit <http://localhost:5000/ui> to
  see the swagger interface, and in a separate tab open to
  <http://localhost:5000/stream>.

### Without Docker

- `cp .env-template .env` and edit to suit your needs.
- Build a virtual environment for development: `_build_venv`
- `deactivate` if already running a virtual environment
- `source _activate`
- Follow `catch` database setup instructions, or start from a previous database
  copy (see Docker notes).
- Run the webapp: `_entrypoint_webapp`
- Run the task workers (woRQers): `_entrypoint_woRQer`
- Once everything is running in dev mode, visit <http://localhost:5000/ui> to
  see the swagger interface, and in a separate tab open to
  <http://localhost:5000/stream>

## Adding New Data

Whether starting from a blank database, or a working copy, you will probably want to add some new data.

1. Follow `catch` library documentation for adding a new data source.

2. Add the source table name to the API's list of allowed sources:

   - `services/apis/src/api/openapi.yaml` at `paths./catch.get.parameters[name=sources].schema.items.enum`.

3. Optionally update tests, e.g., `tests/test_query_moving.py`.

## Testing

Unit tests and tests on a live database are available. Requirements are listed in `requirements.dev.txt`. In addition, a running redis server on port 6379 is required.

Unit tests are based on a temporary postgres instance and simulated data.
First, install the testing requirements using the [test] option:

```
pip install .[test]
```

Then run the tests with pytest:

```
pytest tests
```

Live database tests are in the `live-tests` directory. They require a
configured `.env` file with `DEPLOYMENT_TIER=LOCAL`. The queries rely on
Catalina, Spacewatch, NEAT, PanSTARRS, and SkyMapper data.

```
pytest live-tests
```
