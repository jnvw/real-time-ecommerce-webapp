# Redis Troubleshooting Guide

## Issue: Shared Cart and Chat Not Working

If shared cart updates and chat functionality are not working, Redis might not be properly configured.

## Step 1: Verify Redis is Configured in Railway

1. Go to Railway Dashboard → Your Project
2. Check if you have a **Redis service** added
3. If not, add one:
   - Click "+ New" → "Database" → "Add Redis"
   - Railway will automatically provide `REDIS_URL`

## Step 2: Check Environment Variables

In Railway → Your Service → Variables, verify you have:
- `REDIS_URL` - Should be set automatically by Railway if Redis service exists
- `REDIS_PUBLIC_URL` - Optional, for external access

**Important**: Make sure `REDIS_URL` is set (not just `REDIS_PUBLIC_URL`)

## Step 3: Check Railway Logs

After deployment, check logs for:
- Any Redis connection errors
- Messages about channel layers
- WebSocket connection errors

Look for errors like:
- "Error connecting to Redis"
- "InMemoryChannelLayer" warnings
- WebSocket connection failures

## Step 4: Verify Redis Connection Format

Railway Redis URLs typically look like:
```
redis://default:password@hostname:port
```

The updated settings should handle this automatically.

## Step 5: Test Redis Connection

You can test if Redis is working by:

1. **Check if WebSocket connects**:
   - Open browser DevTools → Network → WS (WebSocket)
   - Join a group
   - You should see a WebSocket connection to `/ws/group/{secret_code}/`
   - Status should be "101 Switching Protocols"

2. **Test shared cart**:
   - Open the same group in two different browser tabs/windows
   - Add an item to cart in one tab
   - It should appear in the other tab automatically

3. **Test chat**:
   - Send a message in one tab
   - It should appear in other tabs

## Common Issues:

### Issue 1: Using InMemoryChannelLayer
**Symptom**: Works locally but not on Railway, or only works for single user

**Solution**: Make sure `REDIS_URL` is set in Railway environment variables

### Issue 2: Redis URL Format
**Symptom**: Connection errors in logs

**Solution**: The updated settings should handle Railway's Redis URL format automatically

### Issue 3: WebSocket Not Connecting
**Symptom**: No WebSocket connection in browser DevTools

**Possible causes**:
- CSRF issues (should be fixed)
- WebSocket routing not configured (should be working)
- Daphne not handling WebSockets (should be working)

### Issue 4: Redis Service Not Running
**Symptom**: Connection timeouts

**Solution**: 
- Check if Redis service is running in Railway
- Restart Redis service if needed
- Verify `REDIS_URL` points to correct Redis instance

## Quick Fix:

1. **Ensure Redis service exists in Railway**
2. **Verify `REDIS_URL` environment variable is set**
3. **Redeploy your application**
4. **Check logs for Redis connection success**

## After Fixing:

Once Redis is working, you should see:
- Real-time cart updates across all group members
- Chat messages appearing instantly
- Notifications when items are added/removed

If issues persist, check Railway logs for specific error messages.

