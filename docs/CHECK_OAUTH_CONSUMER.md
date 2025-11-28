# Check Your OAuth Consumer Settings

## Error: "oauth_callback must be set to 'oob'"

This error means one of two things:

### Possibility 1: Consumer Registered with "oob"

Your OAuth consumer might have been registered with **"oob"** (out-of-band) instead of a callback URL.

**Check your consumer:**
1. Go to: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration
2. Find your consumer with key: `ff02bad2706bef15385eec1471ee03ea`
3. Click "Update" or "Manage"
4. Check the **"OAuth 'callback' URL"** field:
   - ❌ If it says **"oob"** → That's the problem!
   - ✅ If it says **"http://localhost:5000/api/user/oauth/callback"** → That's correct

**If it's set to "oob":**
- You have two options:
  1. **Update the consumer** (if possible) to use: `http://localhost:5000/api/user/oauth/callback`
  2. **OR** set `OAUTH_USE_OOB=True` in your `.env` file

### Possibility 2: Callback URL Mismatch

The callback URL being sent doesn't match what's registered.

**What to check:**
1. Your consumer should be registered with: `http://localhost:5000/api/user/oauth/callback`
2. The code should be sending: `http://localhost:5000/api/user/oauth/callback`
3. They must match EXACTLY (including http vs https, localhost vs 127.0.0.1)

**To debug:**
1. Check Flask console logs when you click "Login with Wikimedia"
2. Look for: `Using OAuth callback URL: ...`
3. Verify it matches your registered callback URL exactly

## Quick Fix

If your consumer is registered with "oob", update your `.env`:

```env
OAUTH_USE_OOB=True
```

Then restart Flask and try again. You'll need to manually enter a verification code.

## Better Solution

Create a NEW consumer with the correct callback URL:
1. Go to: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration
2. Register NEW consumer with callback: `http://localhost:5000/api/user/oauth/callback`
3. Update `.env` with new credentials
4. Keep `OAUTH_USE_OOB=False`

