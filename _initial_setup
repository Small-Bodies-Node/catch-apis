#!/usr/bin/env false

### 0. Load vars defined in .env
if [ ! -f $PWD/.env ]; then
    echo -e "No .env file found!!!"
    return 1
fi
source .env

### 1. Message user
clear
echo -e """${GRE}
=======================================
Initializing Python Virtual Environment
=======================================
${WHI}"""

sleep 1

### 2. Get rid of caches NOT in .venv
find . -type d ! -path './.venv/*' -name '__pycache__' -exec rm -rf {} +
find . -type d ! -path './.venv/*' -name '.pytest_cache' -exec rm -rf {} +
find . -type d ! -path './.venv/*' -name '.mypy_cache' -exec rm -rf {} +

### 3. Check for existence of `.venv` dir
if [[ ! -d $PWD/.venv ]]; then
    echo -e """${BLU}
    virtual Environment Not Found -- Creating '.venv'
"""
    $PYTHON_3_7_OR_HIGHER -m venv .venv --prompt=$APP_NAME
fi

### 4. Activate VENV
source ./.venv/bin/activate

### 5. libs2
if [[ ! -e $VIRTUAL_ENV/lib/libs2.so ]]; then
    echo -e """${BLU}
    installing libs2
${WHI}
"""
    bash _install_s2
fi

### 6. Install python package dependencies for project

# Compiler settings
# Set LDFLAGS to use libs2 in our virtual environment
LDFLAGS="-L$VIRTUAL_ENV/lib -Wl,-rpath=$VIRTUAL_ENV/lib"

pip install --upgrade -q -q -q setuptools wheel cython
pip install -q -r requirements.vscode.txt
pip install -q -r requirements.txt

### 7. Link git pre-commit-hook script
ln -fs $PWD/_precommit_hook $PWD/.git/hooks/pre-commit

### 8. Create logging directories
mkdir -p logging/old-logs

### 9. Final Message
echo -e """${BLU}
    Done. Bon courage!
${WHI}
"""
