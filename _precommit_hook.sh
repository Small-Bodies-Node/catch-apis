#! /bin/bash

echo '''

    ======================
    RUNNING PRECOMMIT HOOK
    ======================

'''

echo $#
echo $1
echo $2
echo $3
echo $4

.venv/bin/autopep8 -ir src/**
