#!/bin/bash
set -e

echo "Initializing PostgreSQL database..."

# Wait for PostgreSQL to be ready
until pg_isready -h postgres -p 5432 -U postgres; do
  echo "Waiting for PostgreSQL to be ready..."
  sleep 2
done

# Create database and user if they don't exist
psql -h postgres -p 5432 -U postgres -d postgres <<-EOSQL
  CREATE USER banking_user WITH PASSWORD 'banking_password';
  CREATE DATABASE banking_core;
  GRANT ALL PRIVILEGES ON DATABASE banking_core TO banking_user;
  ALTER DATABASE banking_core OWNER TO banking_user;
EOSQL

echo "PostgreSQL database initialized!"