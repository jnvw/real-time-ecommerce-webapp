# Quick Data Migration Steps

## On Your Local Machine (Windows PowerShell)

```powershell
# 1. Navigate to your project
cd D:\webseries\movies\djnagoegem\collab_commerce

# 2. Activate virtual environment
.\env\Scripts\activate

# 3. Export all data (excluding system tables)
python manage.py dumpdata --exclude contenttypes --exclude auth.Permission --exclude sessions --natural-foreign --natural-primary --indent=2 > data_export.json

# 4. Export users separately (important for superuser)
python manage.py dumpdata auth.user --indent=2 > users.json

# 5. Export shop data
python manage.py dumpdata shop --natural-foreign --natural-primary --indent=2 > shop_data.json
```

## On Railway

### Option 1: Using Railway Web Terminal

1. Go to Railway Dashboard → Your Service → Deployments → Click on latest deployment
2. Click "View Logs" or find "Connect" button
3. Run these commands:

```bash
# First, ensure migrations are applied
python manage.py migrate

# Import users first
python manage.py loaddata users.json

# Then import shop data
python manage.py loaddata shop_data.json

# Or import everything at once (if you exported all)
python manage.py loaddata data_export.json
```

### Option 2: Using Railway CLI

```bash
# Install Railway CLI (if not installed)
npm i -g @railway/cli

# Login
railway login

# Link your project
railway link

# Upload and run (you'll need to copy the JSON content)
railway run python manage.py loaddata data_export.json
```

## Verify Redis is Working

Check your Railway logs - you should see the app starting without Redis warnings. If you see "WARNING: Redis not configured", make sure `REDIS_URL` is set in Railway environment variables.

## Handle Media Files (Images)

Your product images need to be uploaded separately. Options:

1. **Use Railway Volumes** (if configured)
2. **Use Cloud Storage** (recommended - AWS S3, Cloudinary, etc.)
3. **Manual upload** via Railway file system (if accessible)

For now, your app will work but images might be missing until you upload them.

