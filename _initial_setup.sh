#! /usr/bin/env false
#
# Set up environment for developing/running catch-apis.
# Always run this in ANY new window before doing ANYTHING!

clear

### 0. Load vars defined in .env
if [[ -f .env ]]; then
  source .env
else
  echo """
    ===================================
    No .env file found! Failing set up.
    Copy and edit from '.env-template'
    ===================================
  """
  return 1
fi

### 1. Print what's happening
echo -e """${CYA}
    =======================================
    Initializing Python Virtual Environment
    =======================================
${WHI}"""
sleep 1

### 2. Get rid of cached versions
rm -rf .mypy_cache
find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

### 3. Make sure there's a .config.cfg file for flask_dashboardmonitor
if [[ ! -f .config.cfg ]]; then
  echo -e """${RED}
    =============================================================================
    No '.config.cfg' file found! Exiting set up.
    A template can be found here:
    https://flask-monitoringdashboard.readthedocs.io/en/master/configuration.html
    =============================================================================
  ${WHI}"""
  return 1
fi

### 4. Make sure there's a DB file for flask_dashboardmonitor
if [[ ! -f .dashboard.db ]]; then
  echo -e "${CYA}>>> No file '.dashboard.db' found; creating now${WHI}"
  touch .dashboard.db
fi

### 5. Ensure existence of `.venv` dir
if [[ ! -d ./.venv ]]; then
  echo -e "${CYA}>>> Virtual Environment Not Found -- Creating './.venv'${WHI}"
  $PYTHON_3_5_OR_HIGHER -m venv .venv
fi

### 6. Activate VENV
source ./.venv/bin/activate

### 7. Upgrade pip
pip install --upgrade pip

### 8. Install Requirements to VENV
echo "${CYA}>>> Installing python packages...${WHI}"
sleep 1
pip install -r requirements.vscode.txt
pip install -r requirements.txt

### 9. Link git pre-commit-hook script
ln -fs $PWD/_precommit_hook $PWD/.git/hooks/pre-commit

### 10. Check that redis dirs exist and give status of redis:
echo "${CYA}>>> Install and start redis if it's not already running; its status is:${WHI}"
if [[ ! -d .redis ]]; then mkdir -p .redis; fi
if [[ ! -d .redis/old-logs ]]; then mkdir -p .redis/old-logs; fi
./_redis_manager status

### 11. Ensure npm is installed and required packages are globally available
if [ $(command -v npm) ]; then
  echo -e "${CYA}>>> Checking/installing required npm packages${WHI}"
  if [ $(command -v nodemon) ]; then
    echo -e "${CYA}>>> nodemon found${WHI}"
  else
    echo -e "${CYA}>>> nodemon not found; installing:${WHI}"
    npm install -g nodemon
  fi
  if [ $(command -v pm2) ]; then
    echo -e "${CYA}>>> pm2 found${WHI}"
  else
    echo "${CYA}>>> pm2 not found; installing:${WHI}"
    npm install -g pm2
  fi
else
  echo -e "${RED}No npm found!!!${WHI}"
  return 1
fi

### 12. Ensure we have dirs for web-api logging in production
if [[ ! -d logging/old-logs ]]; then mkdir -p logging/old-logs; fi

### 13. Inject custom html into flask_restplus templates
./_customize_swagger

echo -e "${GRE}>>> Set up complete. Enjoy Flask API-ing!${WHI}"
