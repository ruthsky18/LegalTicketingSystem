#!/bin/bash
# Simplified startup script with better error visibility

echo "=========================================="
echo "Starting Django Application on Railway"
echo "=========================================="

# Show environment info
echo ""
echo "Environment check:"
echo "  PORT: ${PORT:-NOT SET}"
echo "  SECRET_KEY: ${SECRET_KEY:+SET (length: ${#SECRET_KEY})}"
echo "  DEBUG: ${DEBUG:-NOT SET}"
echo "  ALLOWED_HOSTS: ${ALLOWED_HOSTS:-NOT SET}"
echo "  PGHOST: ${PGHOST:-NOT SET}"
echo "  PGDATABASE: ${PGDATABASE:-NOT SET}"
echo "  PGUSER: ${PGUSER:-NOT SET}"
echo "  PGPASSWORD: ${PGPASSWORD:+SET (length: ${#PGPASSWORD})}"
echo ""

# Test Django import first
echo "Testing Django import..."
python -c "import django; print(f'Django {django.get_version()} imported OK')" || {
    echo "ERROR: Failed to import Django"
    exit 1
}

# Test settings import
echo "Testing Django settings..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lrms_project.settings')
import django
django.setup()
print('Django settings loaded OK')
" || {
    echo "ERROR: Failed to load Django settings"
    echo "This is the actual error - check above for details"
    exit 1
}

# Test WSGI import
echo "Testing WSGI application..."
python -c "
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lrms_project.settings')
from lrms_project.wsgi import application
print('WSGI application imported OK')
" || {
    echo "ERROR: Failed to import WSGI application"
    echo "This is the actual error - check above for details"
    exit 1
}

# Run migrations (non-blocking)
echo ""
echo "Running database migrations..."
python manage.py migrate --noinput || {
    echo "WARNING: Migrations failed - continuing anyway"
}

# Start Gunicorn
echo ""
echo "=========================================="
echo "Starting Gunicorn server..."
echo "=========================================="
echo "Port: ${PORT:-8000}"
echo ""

# Use PORT if set, otherwise default to 8000
PORT=${PORT:-8000}
exec gunicorn lrms_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level info --access-logfile - --error-logfile -
