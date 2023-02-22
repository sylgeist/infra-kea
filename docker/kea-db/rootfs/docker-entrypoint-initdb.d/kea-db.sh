#!/usr/bin/env bash
set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
	CREATE USER $KEA_DB_USER WITH PASSWORD '$KEA_DB_USER_PASSWORD';
	CREATE DATABASE $KEA_DB;
	GRANT ALL PRIVILEGES ON DATABASE $KEA_DB TO $KEA_DB_USER;
EOSQL
