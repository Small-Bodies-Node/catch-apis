#! /bin/bash

echo '''

    ======================
    RUNNING PRECOMMIT HOOK
    ======================

'''

.venv/bin/autopep8 -dr src/**
