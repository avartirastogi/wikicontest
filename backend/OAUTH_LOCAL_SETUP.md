# OAuth 1.0a Local Development Setup Guide

This guide will help you set up OAuth 1.0a authentication for local development.

## Step 1: Register OAuth Consumer for Local Development

1. **Go to Wikimedia OAuth Consumer Registration:**
   - Visit: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration

2. **Fill in the registration form:**
   - **Application name:** WikiContest Local Development (or any name you prefer)
   - **Application description:** Local development instance of WikiContest
   - **OAuth "callback" URL:** `http://localhost:5000/api/user/oauth/callback`
     - **IMPORTANT:** This must match exactly, including the protocol (http) and port (5000)
   - **Contact email:** Your email address
   - **Grant settings:** Request authorization for "Basic rights" (or the permissions you need)

3. **Submit the form** and copy the credentials:
   - **Consumer Key** (starts with something like `3f383c834a07a181723f1a1de566f7cf`)
   - **Consumer Secret** (a long hexadecimal string)

## Step 2: Update Your .env File

Update your `backend/.env` file with the new credentials:

```env
# OAuth 1.0a Configuration
OAUTH_MWURI=https://meta.wikimedia.org/w/index.php
CONSUMER_KEY=your-new-consumer-key-here
CONSUMER_SECRET=your-new-consumer-secret-here

# OAuth Callback Configuration
# Set to False for local development with callback URL
OAUTH_USE_OOB=False
```

## Step 3: Test OAuth Login

1. **Start your Flask server:**
   ```bash
   cd backend
   python app.py
   ```

2. **Open your browser:**
   - Go to: http://localhost:5000
   - Click "Login" 
   - Click "Login with Wikimedia"

3. **Authorize the application:**
   - You'll be redirected to Wikimedia
   - Log in with your Wikimedia account (if not already logged in)
   - Click "Allow" to authorize the application

4. **You should be redirected back:**
   - After authorization, you'll be redirected to: `http://localhost:5000/api/user/oauth/callback`
   - The app will process the OAuth callback and log you in
   - You'll be redirected to the home page, logged in

## Troubleshooting

### Error: "oauth_callback must be set to oob"
- **Cause:** Your OAuth consumer was registered with "oob" (out-of-band) instead of a callback URL
- **Solution:** Register a new OAuth consumer with the callback URL: `http://localhost:5000/api/user/oauth/callback`

### Error: "Invalid redirect URI" or "Callback URL mismatch"
- **Cause:** The callback URL in your OAuth consumer registration doesn't match what the app is sending
- **Solution:** 
  1. Check your OAuth consumer registration at: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration
  2. Make sure the callback URL is exactly: `http://localhost:5000/api/user/oauth/callback`
  3. If it's different, either:
     - Update the OAuth consumer registration, OR
     - Update `OAUTH_CALLBACK_PATH` in your `.env` file to match

### Error: "OAuth not configured"
- **Cause:** Missing CONSUMER_KEY or CONSUMER_SECRET in .env file
- **Solution:** Make sure both are set in your `.env` file

### OAuth callback returns 404
- **Cause:** The route `/api/user/oauth/callback` is not accessible
- **Solution:** 
  1. Make sure the Flask app is running
  2. Check that the blueprint is registered: `app.register_blueprint(user_bp, url_prefix='/api/user')`
  3. Verify the route exists in `routes/user_routes.py`

## Notes

- **Separate OAuth Consumers:** You can have different OAuth consumers for:
  - Local development: `http://localhost:5000/api/user/oauth/callback`
  - Production/Toolforge: `https://wikicontest.toolforge.org/oauth/callback`
  
- **OAuth Consumer Approval:** New OAuth consumers may need to be approved by Wikimedia administrators. This usually happens automatically for basic rights, but can take a few minutes.

- **Testing:** You can test the OAuth flow without affecting your production OAuth consumer by creating a separate consumer for local development.

