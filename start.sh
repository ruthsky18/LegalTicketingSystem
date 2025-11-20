#!/bin/bash
# Don't exit on errors for migrations/superuser - let Gunicorn start
set -e

echo "Running database migrations..."
if ! python manage.py migrate --noinput; then
    echo "ERROR: Migrations failed! Check database connection."
    echo "Continuing anyway - application may not work correctly."
fi

echo "Creating superuser if needed..."
if ! python scripts/create_superuser.py; then
    echo "WARNING: Superuser creation failed or skipped."
    echo "You can create superuser manually later."
fi

echo "Starting Gunicorn server..."
exec gunicorn lrms_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

