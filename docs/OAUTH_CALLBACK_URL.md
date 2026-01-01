# OAuth Callback URL for Local Development

Quick reference guide for the exact OAuth callback URL to use when registering an OAuth consumer for local development.

---

## Exact Callback URL

Use this **exact** callback URL when registering your OAuth consumer:
```
http://localhost:5000/api/user/oauth/callback
```


## URL Components

| Component    | Value                      | Notes |
|--------------|----------------------------|-------|
| **Protocol** | `http://`                  | NOT `https://` |
| **Host**     | `localhost`                | NOT `127.0.0.1` or any domain name |
| **Port**     | `5000`                     | Must match your Flask server port |
| **Path**     | `/api/user/oauth/callback` | Exact path, no trailing slash |


## Custom Port Configuration

If your Flask server runs on a different port, adjust the callback URL accordingly:

**Example for port 8000:**
```
http://localhost:8000/api/user/oauth/callback
```

**Example for port 3000:**
```
http://localhost:3000/api/user/oauth/callback
```

## OAuth Consumer Registration

When completing the OAuth consumer registration form on Wikimedia Meta:

**Field: OAuth "callback" URL**
```
http://localhost:5000/api/user/oauth/callback
```

**Field: Allow consumer to specify a callback in requests**
- Leave this **unchecked** (No)

## Why This URL?

This callback URL matches the route structure in your Flask application:
```python
# Blueprint registration: /api/user
app.register_blueprint(user_bp, url_prefix='/api/user')

# Route definition: /oauth/callback
@user_bp.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    # OAuth callback handler
```

**Combined path:** `/api/user` + `/oauth/callback` = `/api/user/oauth/callback`


## Common Mistakes

###  Incorrect URLs

| Wrong URL | Issue |
|-----------|-------|
| `https://localhost:5000/api/user/oauth/callback` | Using `https://` instead of `http://` |
| `http://127.0.0.1:5000/api/user/oauth/callback` | Using IP address instead of `localhost` |
| `http://localhost:5000/oauth/callback` | Missing `/api/user` prefix |
| `http://localhost/api/user/oauth/callback` | Missing port number (`:5000`) |
| `http://localhost:5000/api/user/oauth/callback/` | Extra trailing slash |
| `https://wikicontest.toolforge.org/oauth/callback` | Using production URL for local development |

###  Correct URL
```
http://localhost:5000/api/user/oauth/callback
```

---

## Post-Registration Steps

After successfully registering your OAuth consumer:

1. **Copy the credentials:**
   - Consumer Key
   - Consumer Secret

2. **Update your configuration file:**

   **File: `backend/.env`**
```env
   CONSUMER_KEY=your-consumer-key-here
   CONSUMER_SECRET=your-consumer-secret-here
   OAUTH_USE_OOB=False
```

3. **Restart the Flask server:**
```bash
   cd backend
   python app.py
```

4. **Test OAuth authentication:**
   - Navigate to `http://localhost:5000`
   - Click "Login with Wikimedia"
   - Authorize the application
   - Verify successful redirect and login

---

## Troubleshooting

### Callback URL Mismatch Error

If you receive a "callback URL mismatch" error:

1. Verify the registered callback URL in your OAuth consumer settings
2. Ensure it exactly matches: `http://localhost:5000/api/user/oauth/callback`
3. Check that your Flask server is running on port `5000`
4. Confirm `OAUTH_USE_OOB=False` in your `.env` file

### 404 Error on Callback

If the callback returns a 404 error:

1. Verify the Flask server is running
2. Check that the user blueprint is registered with the correct prefix
3. Confirm the route exists in `routes/user_routes.py`

---

## Related Documentation

- For production deployment, see: **OAuth Configuration for Toolforge Deployment**
- For general OAuth setup, see: **OAuth 1.0a Local Development Setup Guide**