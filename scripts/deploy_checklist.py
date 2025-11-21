#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Deployment Checklist Script for UAT
This script helps verify that your deployment is ready.
"""
import os
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

def check_file_exists(filepath, description):
    """Check if a file exists."""
    path = Path(filepath)
    if path.exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description}: {filepath} - NOT FOUND")
        return False

def check_file_content(filepath, content_check, description):
    """Check if file contains specific content."""
    path = Path(filepath)
    if not path.exists():
        print(f"❌ {description}: File not found")
        return False
    
    try:
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            if content_check in content:
                print(f"✅ {description}: {filepath}")
                return True
            else:
                print(f"⚠️  {description}: {filepath} - May need attention")
                return False
    except Exception as e:
        print(f"❌ {description}: Error reading file - {e}")
        return False

def main():
    """Run deployment checklist."""
    print("=" * 60)
    print("🚀 UAT Deployment Checklist")
    print("=" * 60)
    print()
    
    all_checks = []
    
    # Check required files
    print("📁 Required Files:")
    print("-" * 60)
    all_checks.append(check_file_exists("requirements.txt", "Requirements file"))
    all_checks.append(check_file_exists("Procfile", "Procfile"))
    all_checks.append(check_file_exists("start.sh", "Start script"))
    all_checks.append(check_file_exists("nixpacks.toml", "Nixpacks config"))
    all_checks.append(check_file_exists("runtime.txt", "Python runtime version"))
    all_checks.append(check_file_exists("manage.py", "Django manage.py"))
    all_checks.append(check_file_exists("lrms_project/settings.py", "Django settings"))
    print()
    
    # Check configuration
    print("⚙️  Configuration Checks:")
    print("-" * 60)
    all_checks.append(check_file_content("Procfile", "web:", "Procfile has web process"))
    all_checks.append(check_file_content("start.sh", "gunicorn", "Start script uses Gunicorn"))
    all_checks.append(check_file_content("start.sh", "$PORT", "Start script uses PORT variable"))
    all_checks.append(check_file_content("requirements.txt", "gunicorn", "Gunicorn in requirements"))
    all_checks.append(check_file_content("requirements.txt", "whitenoise", "WhiteNoise in requirements"))
    print()
    
    # Check settings.py
    print("🔧 Django Settings Checks:")
    print("-" * 60)
    try:
        with open("lrms_project/settings.py", 'r', encoding='utf-8', errors='replace') as f:
            settings_content = f.read()
            
        checks = [
            ("SECRET_KEY", "SECRET_KEY configuration"),
            ("DEBUG", "DEBUG configuration"),
            ("ALLOWED_HOSTS", "ALLOWED_HOSTS configuration"),
            ("whitenoise", "WhiteNoise middleware"),
            ("postgresql", "PostgreSQL database support"),
        ]
        
        for check, description in checks:
            if check.lower() in settings_content.lower():
                print(f"✅ {description}")
                all_checks.append(True)
            else:
                print(f"⚠️  {description} - Check manually")
                all_checks.append(False)
    except Exception as e:
        print(f"❌ Error checking settings.py: {e}")
        all_checks.append(False)
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"📊 Summary: {passed}/{total} checks passed ({percentage:.1f}%)")
    print("=" * 60)
    
    if passed == total:
        print("✅ All checks passed! You're ready to deploy.")
    elif passed >= total * 0.8:
        print("⚠️  Most checks passed. Review warnings above.")
    else:
        print("❌ Several checks failed. Please fix issues before deploying.")
    print()
    
    # Next steps
    print("📝 Next Steps:")
    print("-" * 60)
    print("1. Review Railway deployment guide: docs/UAT_DEPLOYMENT_GUIDE.md")
    print("2. Ensure all code is committed to Git")
    print("3. Create Railway account at https://railway.app/signup")
    print("4. Follow the step-by-step deployment guide")
    print("5. Test your deployment after it goes live")
    print()

if __name__ == '__main__':
    main()

