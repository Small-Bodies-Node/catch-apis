
import multiprocessing
import setproctitle

workers = 3  # multiprocessing.cpu_count() * 2 + 1

# NOTE: some gunicorn params (e.g. --name) dont seem to work from here so must be called from the command line
