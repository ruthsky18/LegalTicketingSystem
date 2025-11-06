#!/bin/bash
set -e

echo "Running database migrations..."
python manage.py migrate --noinput

echo "Creating superuser if needed..."
python create_superuser.py

echo "Starting Gunicorn..."
exec gunicorn lrms_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

