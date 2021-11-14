#!/bin/bash

clear
echo "================"
echo "$POSTGRES_DB size:"
echo "================"
psql -U $POSTGRES_USER -d $POSTGRES_DB -c "SELECT pg_size_pretty(pg_database_size('$POSTGRES_DB'));"
echo "================"
