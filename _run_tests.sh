#! /bin/bash

if [ "$1" == "fail" ] ; then
    pytest --junit-xml=pytest_unit.xml
else
    pytest --junit-xml=pytest_unit.xml --ignore=./tests/test_will_fail.py
fi

