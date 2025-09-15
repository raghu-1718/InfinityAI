#!/bin/sh

# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is up!"

# Run database migrations/initializations
echo "Running database initializations..."
poetry run python shared/utils/init_db.py
echo "Database initializations complete."

# Execute the main command (passed from the Dockerfile's CMD)
exec "$@"