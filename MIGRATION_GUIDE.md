# Data Migration Guide: SQLite to PostgreSQL

This guide will help you migrate your data (including users, products, images, etc.) from your local SQLite database to Railway's PostgreSQL database.

## Prerequisites

1. Your local SQLite database with all data (`collab_commerce/db.sqlite3`)
2. Railway PostgreSQL database already set up (DATABASE_URL environment variable)
3. Access to your local development environment

## Step 1: Export Data from SQLite (Local)

Run this on your **local machine** where your SQLite database exists:

```bash
# Navigate to your project directory
cd collab_commerce

# Activate your virtual environment (if using one)
# On Windows:
.\env\Scripts\activate
# On Linux/Mac:
source env/bin/activate

# Export all data to JSON
python manage.py dumpdata --exclude contenttypes --exclude auth.Permission --exclude sessions --natural-foreign --natural-primary --indent=2 > data_export.json
```

**Alternative: Export specific apps only (recommended for large databases):**

```bash
# Export only your app data
python manage.py dumpdata shop --natural-foreign --natural-primary --indent=2 > shop_data.json
python manage.py dumpdata auth.user --indent=2 > users.json
```

## Step 2: Transfer Files to Railway

You have a few options:

### Option A: Using Railway CLI (Recommended)

1. Install Railway CLI if you haven't:
   ```bash
   npm i -g @railway/cli
   ```

2. Login to Railway:
   ```bash
   railway login
   ```

3. Link your project:
   ```bash
   railway link
   ```

4. Upload the JSON file:
   ```bash
   railway run --file data_export.json python manage.py loaddata data_export.json
   ```

### Option B: Using Railway Web Interface

1. Go to your Railway project
2. Open your service
3. Go to the "Data" or "Files" section
4. Upload `data_export.json`
5. Use Railway's terminal/console to run the import command

### Option C: Direct Import via Railway Shell

1. Copy the contents of `data_export.json`
2. Go to Railway dashboard → Your service → Deployments → Latest deployment → View Logs
3. Or use Railway's web terminal
4. Run:
   ```bash
   python manage.py loaddata data_export.json
   ```

## Step 3: Import Data to PostgreSQL (On Railway)

Once your JSON file is accessible on Railway, run:

```bash
# On Railway (via CLI or web terminal)
python manage.py loaddata data_export.json
```

Or if you uploaded specific files:
```bash
python manage.py loaddata users.json
python manage.py loaddata shop_data.json
```

## Step 4: Verify Migration

1. Check your Railway logs to ensure no errors
2. Visit your Railway app: `https://shopcircle.up.railway.app`
3. Login with your superuser credentials
4. Verify:
   - Products are showing
   - Images are loading
   - Users can login
   - Orders are present

## Step 5: Handle Media Files (Images)

Your product images are stored in `collab_commerce/media/products/`. You need to upload these to Railway.

### Option A: Use Railway Volumes (Recommended for persistent storage)

1. In Railway, your media files should be in a volume
2. If not, you may need to configure media file storage

### Option B: Use Cloud Storage (Recommended for production)

Update `settings.py` to use cloud storage (AWS S3, Cloudinary, etc.):

```python
# Example with django-storages
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
```

### Option C: Manual Upload via Railway

1. Zip your media folder:
   ```bash
   cd collab_commerce
   zip -r media.zip media/
   ```

2. Upload to Railway and extract

## Troubleshooting

### Issue: "No such table" errors
**Solution:** Make sure migrations are run first:
```bash
python manage.py migrate
```

### Issue: Foreign key constraint errors
**Solution:** Use `--natural-foreign` and `--natural-primary` flags (already included in commands above)

### Issue: Image files not showing
**Solution:** 
1. Ensure media files are uploaded to Railway
2. Check `MEDIA_ROOT` and `MEDIA_URL` settings
3. Verify file permissions

### Issue: Superuser not working
**Solution:** Create a new superuser on Railway:
```bash
python manage.py createsuperuser
```

## Redis Configuration

Redis should already be working if you have `REDIS_URL` set in Railway. To verify:

1. Check Railway logs for "Using Redis: ..." message
2. Test WebSocket connections (if using real-time features)
3. If Redis is not working, check:
   - `REDIS_URL` environment variable is set
   - Redis service is running in Railway
   - Connection string format is correct

## Quick Commands Reference

```bash
# Export (Local)
python manage.py dumpdata --exclude contenttypes --exclude auth.Permission --exclude sessions --natural-foreign --natural-primary --indent=2 > data_export.json

# Import (Railway)
python manage.py loaddata data_export.json

# Create superuser (Railway)
python manage.py createsuperuser

# Run migrations (Railway - should be automatic)
python manage.py migrate
```

## Notes

- The `--natural-foreign` and `--natural-primary` flags ensure foreign keys are exported by their natural keys rather than primary keys, making migration safer
- Always backup your PostgreSQL database before importing
- Large databases may take time to import
- Media files need to be handled separately from database data

