#!/usr/bin/env python
"""
Validate Django configuration before starting Gunicorn.
This helps diagnose startup issues.
"""
import os
import sys

print("=" * 60)
print("Django Configuration Validation")
print("=" * 60)

# Check environment variables
print("\n1. Checking environment variables...")
required_vars = ['SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS']
optional_vars = ['PGHOST', 'PGDATABASE', 'PGUSER', 'PGPASSWORD']

for var in required_vars:
    value = os.environ.get(var, '')
    if value:
        if var == 'SECRET_KEY':
            print(f"  ✅ {var}: Set (length: {len(value)})")
        else:
            print(f"  ✅ {var}: {value}")
    else:
        print(f"  ⚠️  {var}: NOT SET (using default)")

for var in optional_vars:
    value = os.environ.get(var, '')
    if value:
        if var == 'PGPASSWORD':
            print(f"  ✅ {var}: Set (length: {len(value)})")
        else:
            print(f"  ✅ {var}: {value}")
    else:
        print(f"  ⚠️  {var}: NOT SET")

# Try importing Django
print("\n2. Testing Django import...")
try:
    import django
    print(f"  ✅ Django {django.get_version()} imported successfully")
except ImportError as e:
    print(f"  ❌ Failed to import Django: {e}")
    sys.exit(1)

# Try loading settings
print("\n3. Testing Django settings...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lrms_project.settings')

try:
    django.setup()
    print("  ✅ Django settings loaded successfully")
except Exception as e:
    print(f"  ❌ Failed to load Django settings: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try importing WSGI application
print("\n4. Testing WSGI application...")
try:
    from lrms_project.wsgi import application
    print("  ✅ WSGI application imported successfully")
except Exception as e:
    print(f"  ❌ Failed to import WSGI application: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Try database connection
print("\n5. Testing database connection...")
try:
    from django.db import connection
    connection.ensure_connection()
    print("  ✅ Database connection successful")
except Exception as e:
    print(f"  ⚠️  Database connection failed: {e}")
    print("  (This might be okay if database isn't set up yet)")

# Try importing all apps
print("\n6. Testing app imports...")
from django.conf import settings
for app in settings.INSTALLED_APPS:
    if not app.startswith('django.'):
        try:
            __import__(app)
            print(f"  ✅ {app}")
        except Exception as e:
            print(f"  ❌ {app}: {e}")

print("\n" + "=" * 60)
print("✅ Validation complete - Django is ready!")
print("=" * 60)

