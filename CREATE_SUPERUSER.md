# Create Superuser on Railway

## Method 1: Using Railway Web Terminal (Easiest)

1. Go to your Railway Dashboard: https://railway.app
2. Select your project → Select your service
3. Click on the latest deployment
4. Look for "Connect" or "Terminal" button (usually in the top right)
5. Click it to open a terminal
6. Run:
   ```bash
   python manage.py createsuperuser
   ```
7. Follow the prompts:
   - Username: (enter your desired username)
   - Email: (enter your email)
   - Password: (enter a strong password)
   - Password (again): (confirm password)

## Method 2: Using Railway CLI

1. Install Railway CLI (if not installed):
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

4. Run createsuperuser:
   ```bash
   railway run python manage.py createsuperuser
   ```

5. Follow the prompts to create your superuser

## Method 3: Using Railway One-Click Deploy Terminal

1. In Railway dashboard, go to your service
2. Click on "Settings" tab
3. Scroll down to find "Deploy" or "Terminal" section
4. Click "Open Terminal" or "Connect"
5. Run the createsuperuser command

## After Creating Superuser

1. Visit your admin panel:
   ```
   https://shopcircle.up.railway.app/admin/
   ```

2. Login with the credentials you just created

3. You can now:
   - Add products manually
   - Manage users
   - View orders
   - Configure settings

## Troubleshooting

**Issue: "Command not found" or "python not found"**
- Try: `python3 manage.py createsuperuser`
- Or: `python3.11 manage.py createsuperuser`

**Issue: "No such table" errors**
- Make sure migrations are run first:
  ```bash
  python manage.py migrate
  ```

**Issue: Can't access terminal**
- Check if your deployment is active
- Try redeploying if needed
- Use Railway CLI as alternative

