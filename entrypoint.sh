#!/bin/sh
# entrypoint.sh - wait for db, run migrations, collectstatic optionally, then start the app
set -e

# Default values if not provided
DB_HOST=${DB_HOST:-localhost}
DB_PORT=${DB_PORT:-5432}

wait_for_db() {
  echo "Waiting for database at $DB_HOST:$DB_PORT..."
  # Try to open a TCP connection to the DB host/port
  while ! nc -z $DB_HOST $DB_PORT; do
    echo "Database is not ready yet - sleeping 1s"
    sleep 1
  done
}

# Run wait and migrations
wait_for_db

echo "Running Django migrations..."
python manage.py migrate --noinput

# Optionally collectstatic if you need it (uncomment if desired)
# echo "Collecting static files..."
# python manage.py collectstatic --noinput

# Execute the given command (Daphne by default)
exec "$@"
