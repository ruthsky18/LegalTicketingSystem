# Railway Application Failed to Respond - Quick Fix Guide

## 🚨 Current Error
"Application failed to respond" at `https://web-production-53c8a.up.railway.app`

## 📋 Step-by-Step Diagnosis

### Step 1: Check Railway Deployment Logs (Most Important!)

**In Railway Dashboard:**
1. Go to: https://railway.app
2. Click on your **project** (e.g., "reasonable-light")
3. Click on **"web"** service
4. Go to **"Deployments"** tab
5. Click on the **latest deployment** (should show recent timestamp)
6. Click **"View Logs"** button

**Look for these errors:**

❌ **Build Errors:**
- Missing dependencies
- Python version issues
- Installation failures

❌ **Startup Errors:**
- `SECRET_KEY` missing
- `ALLOWED_HOSTS` issues
- Database connection failed
- Gunicorn startup errors

❌ **Migration Errors:**
- Database connection refused
- Migration failures

**Copy the error message** from the logs - this tells us exactly what's wrong!

---

### Step 2: Check Service Logs

**In Railway Dashboard:**
1. **Web service** → **"Logs"** tab
2. Look for recent error messages
3. Scroll to see what happened during startup

**Common errors you might see:**
- `SECRET_KEY` not set
- Database connection failed
- `ALLOWED_HOSTS` error (we fixed this in code)
- Application crash

---

### Step 3: Verify Environment Variables

**In Railway Dashboard:**
1. **Web service** → **"Variables"** tab
2. Check if these exist:

**Required Variables:**
```env
SECRET_KEY=<must-have-a-value>
DEBUG=True
ALLOWED_HOSTS=*
```

**If SECRET_KEY is missing or empty:**
1. Generate a new key locally:
   ```powershell
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```
2. Copy the generated key
3. In Railway: **Web service** → **Variables** → **+ New Variable**
4. Name: `SECRET_KEY`
5. Value: (paste the generated key)
6. Save - Railway will auto-redeploy

**If DEBUG is missing:**
1. **Variables** → **+ New Variable**
2. Name: `DEBUG`
3. Value: `True`
4. Save

**If ALLOWED_HOSTS is missing:**
1. **Variables** → **+ New Variable**
2. Name: `ALLOWED_HOSTS`
3. Value: `*`
4. Save

---

### Step 4: Verify Database Connection

**Check if Postgres is linked:**
1. **Web service** → **Settings** tab
2. Scroll to **"Connected Services"** or **"Service Settings"**
3. Verify **Postgres** is listed

**If Postgres is NOT linked:**
1. Click **"Connect to Database"** or **"Add Database"**
2. Select your **Postgres** service
3. Click **"Connect"**
4. Wait for variables to appear

**Check database variables:**
1. **Web service** → **Variables** tab
2. Look for:
   - `PGHOST` (should exist if database is linked)
   - `PGDATABASE`
   - `PGUSER`
   - `PGPASSWORD`
   - `PGPORT`

**If these are missing:**
- Database isn't linked properly
- Go back and link the database

---

### Step 5: Common Issues and Quick Fixes

#### Issue A: Missing SECRET_KEY
**Error in logs:** `SECRET_KEY` must not be empty

**Fix:**
1. Generate key (see Step 3)
2. Add `SECRET_KEY` variable in Railway
3. Wait for redeploy

#### Issue B: Database Connection Failed
**Error in logs:** `could not connect to server` or `no such table`

**Fix:**
1. Verify Postgres is linked (Step 4)
2. Check database variables exist
3. If missing, link database again
4. Redeploy after linking

#### Issue C: Application Crash on Startup
**Error in logs:** Application starts then crashes immediately

**Fix:**
1. Check all required environment variables are set
2. Verify SECRET_KEY is set
3. Check database connection
4. Review full error in logs

#### Issue D: Build Failed
**Error in logs:** Build errors during dependency installation

**Fix:**
1. Check `requirements.txt` is correct
2. Verify Python version matches `runtime.txt`
3. Check build logs for specific error

#### Issue E: Port Binding Error
**Error in logs:** Port already in use or connection refused

**Fix:**
- Should not happen - Railway sets PORT automatically
- Verify `start.sh` uses `$PORT` variable (it does)

---

### Step 6: Force Redeploy

**If fixes don't work:**

**Option A: Via Railway Dashboard**
1. **Web service** → **Settings** tab
2. Scroll to **"Deploy"** section
3. Click **"Redeploy"** or **"Deploy Now"** button

**Option B: Via Railway CLI**
```powershell
railway up
```

**Option C: Trigger via Git Push**
```powershell
git commit --allow-empty -m "Trigger redeploy"
git push
```

---

### Step 7: Test After Fixes

**After making fixes and redeploying:**

1. Wait 2-3 minutes for deployment to complete
2. Check deployment status: **Web service** → **Deployments** → Latest
3. Verify deployment succeeded (green checkmark)
4. Check logs: **Logs** tab - should see "Application startup complete"
5. Test URL: `https://web-production-53c8a.up.railway.app`

**Success indicators:**
- ✅ Deployment shows "Deployment successful"
- ✅ Logs show Gunicorn started
- ✅ URL shows login page (not error page)

---

## 🔍 Most Likely Issues (In Order)

1. **Missing SECRET_KEY** (most common)
   - Fix: Add SECRET_KEY variable

2. **Database not linked**
   - Fix: Link Postgres database

3. **Missing environment variables**
   - Fix: Add DEBUG and ALLOWED_HOSTS

4. **Database connection failed**
   - Fix: Verify database is linked and variables exist

5. **Build/deployment error**
   - Fix: Check deployment logs for specific error

---

## 🛠️ Quick Diagnostic Commands

**If you have Railway CLI installed:**

```powershell
# View recent logs
railway logs

# Check Django configuration
railway run python manage.py check

# Test database connection
railway run python manage.py dbshell

# Check migrations
railway run python manage.py showmigrations

# View environment variables
railway variables
```

**If using Railway Shell:**
1. **Web service** → Click **"Shell"** or **"Console"**
2. Run commands directly:
   ```bash
   python manage.py check
   python manage.py showmigrations
   ```

---

## 📝 Action Checklist

**Do these now:**

- [ ] Check deployment logs for error message
- [ ] Check service logs for startup errors
- [ ] Verify SECRET_KEY is set in Variables
- [ ] Verify DEBUG is set (True for UAT)
- [ ] Verify ALLOWED_HOSTS is set (use `*` for now)
- [ ] Verify Postgres database is linked
- [ ] Verify database variables exist (PGHOST, PGDATABASE, etc.)
- [ ] Redeploy after fixing issues
- [ ] Test URL after redeploy

---

## 🆘 Still Having Issues?

**Share this information:**
1. Error message from deployment logs
2. Error message from service logs
3. List of environment variables set
4. Whether database is linked

**Resources:**
- **Railway Support**: https://railway.app/help
- **Railway Discord**: https://discord.gg/railway
- **Troubleshooting Guide**: `docs/RAILWAY_TROUBLESHOOTING.md`

---

**Next Step:** Go to Railway dashboard and check the deployment logs. Share the error message you see!

