#!/usr/bin/env bash
set -e

if [ -z ${ANAL_POSTGRES_TEST_DB+x} ]; then
    echo "Variable ANAL_TEST_DB is not set";
    exit 1
fi

psql -v ON_ERROR_STOP=1 --username "$ANAL_POSTGRES_USER" --dbname "$ANAL_POSTGRES_DB" <<-EOSQL
    CREATE DATABASE $ANAL_POSTGRES_TEST_DB;
    GRANT ALL PRIVILEGES ON DATABASE $ANAL_POSTGRES_TEST_DB TO $ANAL_POSTGRES_USER;
EOSQL