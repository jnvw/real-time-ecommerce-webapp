# Create Superuser on Railway - Step by Step

## ✅ EASIEST METHOD: Railway Web Terminal

### Step 1: Open Railway Dashboard
1. Go to https://railway.app
2. Login to your account
3. Select your project (the one with shopcircle.up.railway.app)

### Step 2: Open Terminal
1. Click on your **service** (the web service, not the database)
2. Look for one of these options:
   - **"Connect"** button (usually in top right)
   - **"Terminal"** tab
   - **"Deployments"** → Click latest deployment → **"View Logs"** → Look for terminal option
   - **"Settings"** → Scroll down to find terminal/console option

### Step 3: Run Command
Once the terminal opens, type:
```bash
python manage.py createsuperuser
```

### Step 4: Enter Details
You'll be prompted for:
- **Username**: (choose any username, e.g., "admin")
- **Email address**: (your email)
- **Password**: (choose a strong password)
- **Password (again)**: (confirm password)

### Step 5: Access Admin
1. Go to: https://shopcircle.up.railway.app/admin/
2. Login with your new credentials
3. Start adding your data!

---

## Alternative: If Web Terminal Not Available

### Option A: Use Railway CLI with Correct Path

Make sure you're in the project root and Railway is linked:

```powershell
# Make sure Railway is linked to your project
railway link

# Then run (Railway will execute this in the container)
railway run python manage.py createsuperuser
```

**Note**: Railway CLI runs commands in the container at `/app/`, so `manage.py` should be there automatically.

### Option B: Create Superuser via Django Shell

If terminal access is difficult, you can create a management command:

1. Create a file: `collab_commerce/shop/management/commands/create_superuser.py`
2. Add code to create superuser programmatically
3. Run: `railway run python manage.py create_superuser`

---

## Troubleshooting

### "Command not found" or "python not found"
Try:
```bash
python3 manage.py createsuperuser
```

### "No such table" error
Migrations might not be run. Check logs or run:
```bash
python manage.py migrate
```

### Can't find terminal in Railway
- Look in different tabs: Settings, Deployments, Service
- Try clicking on the service name/icon
- Check Railway's documentation for latest UI changes
- Use Railway CLI as backup

### Railway CLI not working
Make sure:
1. Railway CLI is installed: `npm i -g @railway/cli`
2. You're logged in: `railway login`
3. Project is linked: `railway link`
4. You're in the correct project directory

---

## Quick Reference

**Admin URL**: https://shopcircle.up.railway.app/admin/

**Command**: `python manage.py createsuperuser`

**Location**: Railway Web Terminal (easiest method)

