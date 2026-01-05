# Create Superuser on Railway Free Tier (No Web Terminal)

Since Railway free tier doesn't include web terminal access, use this custom management command.

## Method 1: Using Environment Variables (Easiest)

### Step 1: Add Environment Variables in Railway

1. Go to Railway Dashboard → Your Service
2. Click on **"Variables"** tab
3. Add these three variables:

   ```
   DJANGO_SUPERUSER_USERNAME = admin
   DJANGO_SUPERUSER_EMAIL = your-email@example.com
   DJANGO_SUPERUSER_PASSWORD = your-strong-password-here
   ```

4. **Save** the variables

### Step 2: Run the Command via Railway CLI

After deploying the updated code (with the new management command), run:

```powershell
railway run python manage.py create_superuser --noinput
```

This will create the superuser using the environment variables you set.

### Step 3: Remove Environment Variables (Security)

**Important**: After creating the superuser, **delete** the `DJANGO_SUPERUSER_PASSWORD` variable from Railway for security!

You can keep the username and email if you want, but definitely remove the password.

---

## Method 2: Using Command Arguments

If you prefer not to use environment variables:

```powershell
railway run python manage.py create_superuser --username admin --email your-email@example.com --password your-password --noinput
```

**Note**: This exposes the password in command history, so Method 1 is safer.

---

## Method 3: Interactive Mode (If Railway CLI Supports It)

If Railway CLI allows interactive input:

```powershell
railway run python manage.py create_superuser
```

Then enter the details when prompted.

---

## After Creating Superuser

1. **Remove the password environment variable** from Railway (security best practice)
2. Visit: https://shopcircle.up.railway.app/admin/
3. Login with your credentials
4. Start adding your data!

---

## Troubleshooting

### "Command not found" or "No such command"
- Make sure you've deployed the latest code with the management command
- The command file should be at: `collab_commerce/shop/management/commands/create_superuser.py`

### "A superuser already exists"
- A superuser was already created
- You can create another one by removing `--noinput` and using different username
- Or login with existing superuser

### "Error creating superuser"
- Check Railway logs for detailed error
- Make sure migrations are run: `railway run python manage.py migrate`
- Verify database connection is working

---

## Quick Reference

**Command**: `railway run python manage.py create_superuser --noinput`

**Required Env Vars**:
- `DJANGO_SUPERUSER_USERNAME`
- `DJANGO_SUPERUSER_EMAIL`  
- `DJANGO_SUPERUSER_PASSWORD`

**Admin URL**: https://shopcircle.up.railway.app/admin/

