# Auto-Create Superuser on Railway (Free Tier Solution)

Since Railway free tier doesn't have web terminal and `railway run` executes locally, the startup script will automatically create a superuser during deployment if environment variables are set.

## Steps:

### Step 1: Add Environment Variables in Railway

1. Go to Railway Dashboard → Your Service → **Variables** tab
2. Add these 3 variables:

   ```
   DJANGO_SUPERUSER_USERNAME = admin
   DJANGO_SUPERUSER_EMAIL = your-email@example.com
   DJANGO_SUPERUSER_PASSWORD = your-strong-password-here
   ```

3. **Save** the variables

### Step 2: Deploy

1. Commit and push your code (or Railway will auto-deploy if connected to Git)
2. The startup script will automatically:
   - Run migrations
   - Collect static files
   - **Create superuser** (if env vars are set and no superuser exists)
   - Start the server

### Step 3: Check Logs

After deployment, check Railway logs. You should see:
```
Checking for superuser...
Successfully created superuser "admin"
```

Or if superuser already exists:
```
Superuser creation skipped (may already exist)
```

### Step 4: Access Admin

1. Visit: https://shopcircle.up.railway.app/admin/
2. Login with your credentials
3. Start adding your data!

### Step 5: Remove Password Variable (Security)

**Important**: After the superuser is created, **delete** the `DJANGO_SUPERUSER_PASSWORD` variable from Railway for security!

You can keep username and email, but definitely remove the password after first deployment.

---

## How It Works

The startup script checks if all three environment variables are set:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD`

If all are set, it runs:
```bash
python manage.py create_superuser --noinput
```

This only creates a superuser if one doesn't already exist, so it's safe to keep the variables (except password) for future deployments.

---

## Troubleshooting

### Superuser not created
- Check Railway logs for errors
- Verify all 3 environment variables are set
- Make sure migrations ran successfully
- Check if a superuser already exists

### "Superuser already exists"
- This is normal if you've already created one
- You can login with existing credentials
- To create another, temporarily remove existing superuser or use different username

### Can't login
- Verify credentials are correct
- Check if superuser was actually created (check logs)
- Try creating with different username/email

---

## Security Best Practices

1. **Remove password variable** after first successful deployment
2. Use strong passwords
3. Don't commit environment variables to Git
4. Consider using Railway's secret management for sensitive data

---

## Quick Reference

**Environment Variables Needed**:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`
- `DJANGO_SUPERUSER_PASSWORD` (remove after creation!)

**Admin URL**: https://shopcircle.up.railway.app/admin/

**Automatic**: Happens during deployment, no manual command needed!

