#! /bin/bash

### The main logic of this script is placed in the main() function,
### which is setup to only be run if the script is SOURCE-ed

main()
{
    printf "\n"
    printf "\n"
    printf "======================================================"
    printf "\n"
    printf "\n"
    printf "Initializing Environment"
    printf "\n"
    printf "\n"
    printf "(Make sure you're SOURCE-ING not SH-ing this script!)"
    printf "\n"
    printf "\n"
    printf "======================================================"
    printf "\n"
    printf "\n"

    ### 0. Get rid of cached versions
    rm -rf .mypy_cache
    rm -rf src/__pycache__

    ### 1. Load vars defined in .env 
    eval $(cat .env | sed 's/^/export /')       

    ### 2. Check for existence of `.venv` dir
    if [ ! -d ./.venv ]; then
        echo "Virtual Environment Not Found -- Creating './.venv'"
        $VIRTUALENV --python=$PYTHON_3_5_OR_HIGHER ./.venv
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

    export MYPYPATH=$PWD/stubs
}

unset BASH_SOURCE 2>/dev/null
test ".$0" == ".$BASH_SOURCE" && echo "You must <SOURCE> (not SH) this script!!!" || main "$@"

