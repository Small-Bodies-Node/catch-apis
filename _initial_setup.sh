#! /bin/bash

### The main logic of this script is placed in the main() function;
### We only want the main function to be called if this script is sourced (not sh-ed)
### This script uses a 'trick' to tell if it's being sourced or sh-ed

main() {
    clear

    echo "
    =======================================================

    Initializing Python Virtual Environment

    (Make sure you're SOURCE-ING not SH-ing this script!)

    =======================================================
    "

    sleep 1

    ### 0. Get rid of cached versions
    rm -rf .mypy_cache
    rm -rf src/__pycache__

    ### 1. Load vars defined in .env
    eval $(cat .env | sed 's/^/export /')

    ### 2. Check for existence of `.venv` dir
    if [ ! -d ./.venv ]; then
        echo "Virtual Environment Not Found -- Creating './.venv'"
        # $VIRTUALENV --python=$PYTHON_3_5_OR_HIGHER ./.venv
        $PYTHON_3_5_OR_HIGHER -m venv .venv
    fi

    ### 3. Activate VENV
    source ./.venv/bin/activate

    ### 4. Upgrade pip
    pip install --upgrade pip

    ### 5. Install Requirements to VENV
    pip install -r requirements.txt

    ### 6. Export Misc Env Vars
    ### 6.1. VSCode: Need to include in PYTHONPATH any dirs where you want VSCode to look for modules
    export PYTHONPATH=$PWD/src

    ### 7. Link git pre-commit-hook script
    ln -fs $PWD/_precommit_hook.sh $PWD/.git/hooks/pre-commit
}

if [ $1 = 'jenkins' ]; then
    ## Jenkins will error if you use the trick in the else clause
    echo "Running from jenkins"
    main
else
    ## Trick to check if this script is being sourced or sh-ed
    unset BASH_SOURCE 2>/dev/null
    test ".$0" == ".$BASH_SOURCE" && echo "You must <SOURCE> (not SH) this script!!!" || main "$@"
fi
