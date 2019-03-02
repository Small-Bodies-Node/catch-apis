#! /bin/bash

### Recursively remove all files/dirs containing __pycache__ or .pyc:
find . | grep -E "(__pycache__|\.pyc$)" | xargs rm -rf
