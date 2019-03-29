#! /bin/bash

echo '''
    ==============
    PRECOMMIT HOOK
    ==============
'''

.venv/bin/autopep8 -dr src/**
