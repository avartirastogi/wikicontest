# Create Local OAuth Consumer - Step by Step

## Problem
Your current OAuth consumer is registered for Toolforge:
- Callback URL: `https://wikicontest.toolforge.org/oauth/callback`
- This won't work for localhost!

## Solution: Create a NEW OAuth Consumer for Local Development

### Step 1: Go to OAuth Registration

Visit: **https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration**

### Step 2: Fill Out the Registration Form

**Application name:**
```
WikiContest Local Development
```
(Use a different name from your Toolforge consumer)

**Consumer version:**
```
1.0
```

**OAuth protocol version:**
```
OAuth 1.0a
```
(Must match - your code uses OAuth 1.0a)

**Description:**
```
Local development instance of WikiContest for testing
```

**OAuth "callback" URL:**
```
http://localhost:5000/api/user/oauth/callback
```
⚠️ **CRITICAL:** Must be EXACTLY this:
- Protocol: `http://` (NOT https)
- Host: `localhost` (NOT 127.0.0.1 or toolforge.org)
- Port: `5000` (must match your Flask server port)
- Path: `/api/user/oauth/callback`

**Allow consumer to specify a callback in requests:**
```
No
```
(Leave unchecked)

**Owner-only:**
```
No
```
⚠️ **IMPORTANT:** Make sure this is set to "No" (not "Yes")!

**Applicable grants:**
```
Basic access only
```
(Or whatever permissions you need)

### Step 3: Submit and Copy Credentials

After submission, you'll receive:
- **Consumer key** (hexadecimal string)
- **Consumer secret** (long hexadecimal string)

⚠️ **IMPORTANT:** Copy BOTH immediately! The secret is only shown once!

### Step 4: Update .env File

Open `backend/.env` and update:

```env
CONSUMER_KEY=your-new-local-consumer-key-here
CONSUMER_SECRET=your-new-local-consumer-secret-here
OAUTH_USE_OOB=False
```

Replace with your actual credentials from Step 3.

### Step 5: Restart Flask Server

```bash
cd backend
python app.py
```

### Step 6: Test OAuth Login

1. Go to: http://localhost:5000
2. Click "Login with Wikimedia"
3. Should redirect to Wikimedia, then back to localhost

## Why You Need Separate Consumers

- **Toolforge consumer:** For production (`https://wikicontest.toolforge.org/oauth/callback`)
- **Local consumer:** For development (`http://localhost:5000/api/user/oauth/callback`)

OAuth consumers are tied to their callback URLs and cannot be changed after registration. You need separate consumers for different environments.

## Troubleshooting

### Error: "Invalid redirect URI"
- **Cause:** Callback URL doesn't match
- **Solution:** Verify consumer callback URL is EXACTLY: `http://localhost:5000/api/user/oauth/callback`

### Error: "Owner-only"
- **Cause:** Consumer is set to owner-only
- **Solution:** Create new consumer with "Owner-only: No"

### Still redirecting to Toolforge?
- **Cause:** Using wrong consumer credentials
- **Solution:** Make sure `.env` has the LOCAL consumer credentials, not Toolforge ones

