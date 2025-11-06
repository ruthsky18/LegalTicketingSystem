#!/usr/bin/env python
"""
Script to create a superuser if one doesn't exist.
This runs automatically during deployment.
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'lrms_project.settings')
django.setup()

from django.contrib.auth import get_user_model
from decouple import config

User = get_user_model()

def create_superuser():
    """Create a superuser if one doesn't exist."""
    # Get credentials from environment variables (with defaults)
    username = config('SUPERUSER_USERNAME', default='admin')
    email = config('SUPERUSER_EMAIL', default='admin@example.com')
    password = config('SUPERUSER_PASSWORD', default='admin123')
    
    # Check if superuser already exists
    if User.objects.filter(is_superuser=True).exists():
        print(f"Superuser already exists. Skipping creation.")
        return
    
    # Create superuser
    try:
        User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        print(f"Superuser '{username}' created successfully!")
    except Exception as e:
        print(f"Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser()

