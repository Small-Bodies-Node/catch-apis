# CATCH APIs live database tests

These tests are used on an existing CATCH database. They are designed for the development database (catch_dev on AWS), and may need to be updated as the DEV database changes with time.

## Moving target tests with arbitrary queries

A script is provided to query any target or source. It requires a configured and running instance of the API (i.e., with docker or \_entrypoint_webapp/\_entrypoint_woRQer).

```bash
/test_alive.py --target=65P --source=atlas_mauna_loa
```

An running CATCH instance may be used by setting the `--url` option.

Use `test_alive.py --help` to show other options.

## Programmatic tests

The remaining scripts are used to test the API routes and check the results for expected values. They do not fully cover the code, but do demonstrate that the various routes are generally working.

To run the tests:

1. Setup .env as usual, with DEPLOYMENT_TIER=LOCAL.

2. Create an isolated environment with the CATCH API installed, including requirements for testing, e.g., using the `_build_venv` script. `source .venv/bin/activate` to use it.

3. Run a redis server.

4. Run the tests: `pytest live-db-tests`

To see messages returned from the API: `pytest --capture=tee-sys`
