#!/bin/bash

backup_file=$1

if [[ ! -f $PWD/$backup_file ]]; then
  echo "Backup file '$1' does not exist; exiting"
  return 1
fi

echo """
================================
BEGIN pg_restore

(This might take several mins)

================================
"""

pg_restore -U msk --clean --if-exists -d $POSTGRES_DB "/docker-entrypoint-initdb.d/$backup_file"

# Temp: add extra indices
psql -U $DB_USERNAME -c "create index on observation (source, mjd_start);" $DB_DATABASE
psql -U $DB_USERNAME -c "create index on observation (source, mjd_stop);" $DB_DATABASE

echo """
================================
END pg_restore
================================
"""
