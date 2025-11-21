#!/bin/bash
# Don't use set -e - we want to see all errors, not exit on first failure

echo "=========================================="
echo "Starting Django Application on Railway"
echo "=========================================="

# Show environment info
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

# Validate Django configuration first
echo "Validating Django configuration..."
python scripts/validate_django.py || {
    echo "❌ Django configuration validation failed!"
    echo "Check the errors above and fix them before starting Gunicorn."
    echo ""
    echo "Attempting to continue anyway - Gunicorn will show the actual error..."
}

# Run migrations
echo ""
echo "Running database migrations..."
if python manage.py migrate --noinput; then
    echo "✅ Migrations completed successfully"
else
    echo "⚠️  Migrations failed - check database connection"
    echo "Continuing anyway - application may not work correctly"
fi

# Create superuser if needed
echo ""
echo "Creating superuser if needed..."
if python scripts/create_superuser.py; then
    echo "✅ Superuser check completed"
else
    echo "⚠️  Superuser creation failed or skipped"
    echo "You can create superuser manually later"
fi

# Start Gunicorn
echo ""
echo "=========================================="
echo "Starting Gunicorn server..."
echo "=========================================="
echo "Port: ${PORT:-8000}"
echo "Workers: 2"
echo "Timeout: 120"
echo ""

# Use PORT if set, otherwise default to 8000
PORT=${PORT:-8000}
exec gunicorn lrms_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-level debug

