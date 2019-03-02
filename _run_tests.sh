#! /bin/bash

if [ "$1" == "fail" ] ; then
    pytest --junit-xml=pytest_unit.xml
else
    pytest --junit-xml=pytest_unit.xml --ignore=./tests/test_will_fail.py
fi



# if [ $1 = 'jenkins' ]; then
#     ## Jenkins will error if you use the trick in the else clause
#     echo "Running from jenkins"
#     main
# else
#     ## Trick to check if this script is being sourced or sh-ed
#     unset BASH_SOURCE 2>/dev/null
#     test ".$0" == ".$BASH_SOURCE" && echo "You must <SOURCE> (not SH) this script!!!" || main "$@"
# fi

