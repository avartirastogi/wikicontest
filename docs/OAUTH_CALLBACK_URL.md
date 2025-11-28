# OAuth Callback URL for Local Development

## ✅ Exact Callback URL to Use

When registering your OAuth consumer for local development, use this **EXACT** callback URL:

```
http://localhost:5000/api/user/oauth/callback
```

## Breakdown

- **Protocol:** `http://` (NOT `https://`)
- **Host:** `localhost` (NOT `127.0.0.1` or any domain)
- **Port:** `5000` (must match your Flask server port)
- **Path:** `/api/user/oauth/callback` (exact path, no trailing slash)

## If Your Flask Server Uses a Different Port

If your Flask server runs on a different port (e.g., 8000), change the port in the callback URL:

```
http://localhost:8000/api/user/oauth/callback
```

## Registration Form Fields

When filling out the OAuth consumer registration form:

**OAuth "callback" URL:**
```
http://localhost:5000/api/user/oauth/callback
```

**Allow consumer to specify a callback in requests:**
- Leave this **unchecked** (No)

## Why This URL?

This matches the route defined in your Flask application:
- Blueprint: `/api/user` (from `user_bp`)
- Route: `/oauth/callback` (from `@user_bp.route('/oauth/callback')`)
- Full path: `/api/user/oauth/callback`

## Common Mistakes to Avoid

❌ **Wrong:** `https://localhost:5000/api/user/oauth/callback` (using https)
❌ **Wrong:** `http://127.0.0.1:5000/api/user/oauth/callback` (using IP instead of localhost)
❌ **Wrong:** `http://localhost:5000/oauth/callback` (missing `/api/user` prefix)
❌ **Wrong:** `http://localhost/api/user/oauth/callback` (missing port number)
❌ **Wrong:** `https://wikicontest.toolforge.org/oauth/callback` (Toolforge URL, won't work locally)

✅ **Correct:** `http://localhost:5000/api/user/oauth/callback`

## After Registration

1. Copy the **Consumer Key** and **Consumer Secret**
2. Update your `.env` file:
   ```env
   CONSUMER_KEY=your-consumer-key-here
   CONSUMER_SECRET=your-consumer-secret-here
   OAUTH_USE_OOB=False
   ```
3. Restart Flask server
4. Test OAuth login

