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

echo """
================================
END pg_restore
================================
"""
