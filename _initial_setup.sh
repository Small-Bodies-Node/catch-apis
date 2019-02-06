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

    ### 1. Check for existence of VENV
    eval $(cat .env | sed 's/^/export /')       ### Load vars defined in .env 
    if [ ! -d ./.venv ]; then
        echo "Virtual Environment Not Found -- Creating './.venv'"
        virtualenv --python=$PY3 ./.venv
    fi

    ### 2. Activate VENV
    source ./.venv/bin/activate

    ### 3. Upgrade pip
    pip install --upgrade pip

    ### 4. Install Requirements to VENV
    pip install -r requirements.txt
}

unset BASH_SOURCE 2>/dev/null
test ".$0" == ".$BASH_SOURCE" && echo "You must <SOURCE> (not SH) this script!!!" || main "$@"

