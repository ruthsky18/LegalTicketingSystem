# Railway Deployment Troubleshooting

## Application Failed to Respond Error

If you see "Application failed to respond" error, follow these steps:

### Step 1: Check Deployment Logs

1. Go to your Railway project: https://railway.app
2. Click on your **Web service**
3. Go to **"Deployments"** tab
4. Click on the **latest deployment**
5. Click **"View Logs"**

Look for:
- ❌ **Build errors** - Missing dependencies, Python version issues
- ❌ **Migration errors** - Database connection failures
- ❌ **Startup errors** - Gunicorn failures, missing environment variables
- ❌ **Database connection errors** - PostgreSQL not connected

### Step 2: Check Service Logs

1. In your **Web service**, go to **"Logs"** tab
2. Look for recent error messages
3. Common errors:
   - `SECRET_KEY` not set
   - Database connection failed
   - Port binding issues
   - Missing environment variables

### Step 3: Verify Environment Variables

**Required variables:**

1. Go to **Web service** → **"Variables"** tab
2. Verify these exist:
   ```env
   SECRET_KEY=<must-be-set>
   DEBUG=True (or False for production)
   ALLOWED_HOSTS=* (or your specific domain)
   ```

3. **Generate SECRET_KEY if missing:**
   ```powershell
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

### Step 4: Verify Database Connection

1. **Check if Postgres is linked:**
   - **Web service** → **Settings** tab
   - Scroll to **"Connected Services"**
   - Verify **Postgres** is listed

2. **Check database variables:**
   - **Web service** → **Variables** tab
   - Should see: `PGHOST`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`, `PGPORT`
   - If missing, link database: **Settings** → **Connect to Database**

### Step 5: Common Issues and Fixes

#### Issue: Build Fails

**Symptoms:**
- Build logs show errors
- Missing dependencies

**Fix:**
1. Check `requirements.txt` is up to date
2. Verify Python version in `runtime.txt` matches `nixpacks.toml`
3. Check build logs for specific error

#### Issue: Migrations Fail

**Symptoms:**
- Migration errors in logs
- Database connection refused

**Fix:**
1. Verify database is linked
2. Check database variables are set
3. Run migrations manually:
   ```powershell
   railway run python manage.py migrate
   ```

#### Issue: Application Crashes on Startup

**Symptoms:**
- Application starts then crashes
- Gunicorn errors

**Common causes:**
- Missing `SECRET_KEY`
- Database connection failed
- Missing environment variables

**Fix:**
1. Check all required environment variables
2. Verify database connection
3. Check logs for specific error

#### Issue: Port Binding Error

**Symptoms:**
- Port already in use
- Connection refused

**Fix:**
- Railway automatically sets `PORT` variable
- Ensure `start.sh` uses `$PORT` (should be correct)
- Don't hardcode port numbers

### Step 6: Manual Testing Commands

**Using Railway CLI:**

```powershell
# Login
railway login

# Link project
railway link

# View logs
railway logs

# Check migrations
railway run python manage.py showmigrations

# Run migrations
railway run python manage.py migrate

# Test database connection
railway run python manage.py dbshell

# Check Django settings
railway run python manage.py check

# Create superuser
railway run python manage.py createsuperuser
```

**Using Railway Shell:**

1. **Web service** → Click **"Shell"** or **"Console"**
2. Run commands directly:
   ```bash
   python manage.py check
   python manage.py showmigrations
   python manage.py migrate
   ```

### Step 7: Force Redeploy

If fixes don't work:

1. **Web service** → **Settings** tab
2. Scroll to **"Deploy"** section
3. Click **"Redeploy"** or **"Deploy Now"**

Or via CLI:
```powershell
railway up
```

### Step 8: Verify Application Starts

After fixing issues:

1. Wait for deployment to complete
2. Check **Logs** tab for "Application startup complete"
3. Test URL: `https://your-railway-url.up.railway.app`

## Quick Diagnostic Checklist

- [ ] Deployment logs checked
- [ ] Service logs checked
- [ ] Environment variables verified:
  - [ ] `SECRET_KEY` set
  - [ ] `DEBUG` set (True for UAT)
  - [ ] `ALLOWED_HOSTS` set
- [ ] Database linked to web service
- [ ] Database variables present (PGHOST, PGDATABASE, etc.)
- [ ] Migrations run successfully
- [ ] No errors in logs
- [ ] Application starts successfully

## Need Help?

- **Railway Support**: https://railway.app/help
- **Railway Discord**: https://discord.gg/railway
- **Check Project Logs**: Web Service → Logs tab
- **Deployment Logs**: Web Service → Deployments → Latest → View Logs

---

*Troubleshooting Guide - For detailed deployment steps, see UAT_DEPLOYMENT_GUIDE.md*

