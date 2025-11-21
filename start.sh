#!/bin/bash
set -e

echo "=========================================="
echo "Starting Django Application on Railway"
echo "=========================================="

# Validate Django configuration first
echo "Validating Django configuration..."
if python scripts/validate_django.py; then
    echo "✅ Django configuration is valid"
else
    echo "❌ Django configuration validation failed!"
    echo "Check the errors above and fix them before starting Gunicorn."
    echo ""
    echo "Attempting to continue anyway - check logs for specific errors..."
    # Don't exit - let Gunicorn try to start and show the actual error
fi

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
echo "Port: $PORT"
echo "Workers: 2"
echo "Timeout: 120"
echo ""
exec gunicorn lrms_project.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120

