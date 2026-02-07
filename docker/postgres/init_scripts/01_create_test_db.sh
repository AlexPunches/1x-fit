#!/usr/bin/env bash
set -e

if [ -z ${ANAL_TEST_DB+x} ]; then
    echo "Variable ANAL_TEST_DB is not set";
    exit 1
fi

psql -v ON_ERROR_STOP=1 --username "$ANAL_USER" --dbname "$ANAL_DB" <<-EOSQL
    CREATE DATABASE $ANAL_TEST_DB;
    GRANT ALL PRIVILEGES ON DATABASE $ANAL_TEST_DB TO $ANAL_USER;
EOSQL