#! /bin/bash

PYTHON_ENV=DEV nodemon -w 'src/**' -e py,html --exec python src/app_entry.py
