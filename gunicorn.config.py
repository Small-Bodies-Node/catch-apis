import multiprocessing


workers: int = 2
# workers: int = multiprocessing.cpu_count() * 2

# NOTE: some gunicorn params (e.g. --name) dont seem to work from here
# so must be called from the command line
