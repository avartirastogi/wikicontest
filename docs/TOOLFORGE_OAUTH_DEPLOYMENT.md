# OAuth Configuration for Toolforge Deployment

## 📋 Quick Summary

When deploying to Toolforge, you need to change **3 things** for OAuth:

1. **OAuth Consumer Credentials** - Use Toolforge consumer (not local)
2. **Callback Path** - Set `OAUTH_CALLBACK_PATH = "/oauth/callback"`
3. **Callback URL** - Toolforge consumer uses: `https://wikicontest.toolforge.org/oauth/callback`

---

## 🔄 What Changes Between Local and Production

### Local Development (Current Setup)
- **Consumer Key:** `ff02bad2706bef15385eec1471ee03ea` (local consumer)
- **Consumer Secret:** `a4489c9b18609fe8574d62b01794e4b6f1a3e0d9` (local consumer)
- **Callback URL:** `http://localhost:5000/api/user/oauth/callback`
- **OAUTH_CALLBACK_PATH:** (empty/not set - uses default)

### Toolforge Production (What You Need)
- **Consumer Key:** `3f383c834a07a181723f1a1de566f7cf` (Toolforge consumer)
- **Consumer Secret:** `62c40e0fde2377613d1f82b9b7aabc9fe2a73b30` (Toolforge consumer)
- **Callback URL:** `https://wikicontest.toolforge.org/oauth/callback`
- **OAUTH_CALLBACK_PATH:** `/oauth/callback`

---

## 📝 Step-by-Step: Configure OAuth for Toolforge

### Step 1: Verify Your Toolforge OAuth Consumer

Your Toolforge OAuth consumer is already registered:
- **Consumer Key:** `3f383c834a07a181723f1a1de566f7cf`
- **Callback URL:** `https://wikicontest.toolforge.org/oauth/callback`
- **Status:** Approved ✅
- **Owner-only:** No ✅

**Verify at:** https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/update/3f383c834a07a181723f1a1de566f7cf

### Step 2: Update Configuration File

On Toolforge, you'll use `config.toml` (not `.env`). Update it with:

```toml
# OAuth Configuration for Toolforge
OAUTH_MWURI = "https://meta.wikimedia.org/w/index.php"
CONSUMER_KEY = "3f383c834a07a181723f1a1de566f7cf"
CONSUMER_SECRET = "62c40e0fde2377613d1f82b9b7aabc9fe2a73b30"

# OAuth Callback Path - CRITICAL for Toolforge!
# This tells the code to use /oauth/callback instead of /api/user/oauth/callback
OAUTH_CALLBACK_PATH = "/oauth/callback"

# OAuth Callback Type
OAUTH_USE_OOB = false
```

### Step 3: How the Code Works

The code automatically detects the callback path:

**In `backend/routes/user_routes.py` (lines 376-382):**
```python
custom_callback_path = current_app.config.get('OAUTH_CALLBACK_PATH', None)
if custom_callback_path:
    # Use custom callback path (e.g., /oauth/callback for Toolforge)
    callback_url = f"{scheme}://{host}{custom_callback_path}"
else:
    # Use default blueprint route path (for localhost)
    callback_url = f"{scheme}://{host}/api/user/oauth/callback"
```

**When `OAUTH_CALLBACK_PATH = "/oauth/callback"` is set:**
- Code builds: `https://wikicontest.toolforge.org/oauth/callback` ✅
- This matches your Toolforge OAuth consumer registration ✅

**When `OAUTH_CALLBACK_PATH` is empty (localhost):**
- Code builds: `http://localhost:5000/api/user/oauth/callback` ✅
- This matches your local OAuth consumer registration ✅

### Step 4: Route Handling

The route `/oauth/callback` is already set up in `backend/app.py` (line 284):

```python
@app.route('/oauth/callback', methods=['GET'])
def oauth_callback():
    # Redirects to /api/user/oauth/callback with query parameters
    # This handles the Toolforge callback URL
```

This route redirects to the blueprint handler, so the actual processing happens at `/api/user/oauth/callback`.

---

## 🎯 Complete Toolforge Configuration

### File: `config.toml` (on Toolforge)

```toml
# Security (generate new keys for production!)
SECRET_KEY = "your-generated-secret-key-here"
JWT_SECRET_KEY = "your-generated-jwt-secret-key-here"

# Database
SQLALCHEMY_DATABASE_URI = "mysql://username:password@tools-db/database_name"
SQLALCHEMY_TRACK_MODIFICATIONS = false

# JWT Configuration
JWT_ACCESS_TOKEN_EXPires = 86400

# Debug mode (set to false for production)
DEBUG = false

# OAuth Configuration - TOOLFORGE SETTINGS
OAUTH_MWURI = "https://meta.wikimedia.org/w/index.php"
CONSUMER_KEY = "3f383c834a07a181723f1a1de566f7cf"
CONSUMER_SECRET = "62c40e0fde2377613d1f82b9b7aabc9fe2a73b30"

# OAuth Callback Path - MUST BE SET FOR TOOLFORGE
OAUTH_CALLBACK_PATH = "/oauth/callback"

# OAuth Callback Type
OAUTH_USE_OOB = false
```

---

## 📍 Where Changes Are Made

### 1. Configuration File

**Local:** `backend/.env`
```env
CONSUMER_KEY=ff02bad2706bef15385eec1471ee03ea
CONSUMER_SECRET=a4489c9b18609fe8574d62b01794e4b6f1a3e0d9
# OAUTH_CALLBACK_PATH=  (empty - uses default)
```

**Toolforge:** `$HOME/www/python/src/config.toml`
```toml
CONSUMER_KEY = "3f383c834a07a181723f1a1de566f7cf"
CONSUMER_SECRET = "62c40e0fde2377613d1f82b9b7aabc9fe2a73b30"
OAUTH_CALLBACK_PATH = "/oauth/callback"  # MUST SET THIS!
```

### 2. Code (No Changes Needed!)

The code already handles both scenarios:
- ✅ Detects `OAUTH_CALLBACK_PATH` from config
- ✅ Uses it if set, otherwise uses default `/api/user/oauth/callback`
- ✅ Route `/oauth/callback` already exists in `app.py`

**You don't need to change any code!** Just update the configuration.

---

## ✅ Checklist for Toolforge Deployment

- [ ] OAuth consumer registered with: `https://wikicontest.toolforge.org/oauth/callback`
- [ ] `config.toml` has Toolforge consumer credentials
- [ ] `config.toml` has `OAUTH_CALLBACK_PATH = "/oauth/callback"`
- [ ] `OAUTH_USE_OOB = false` in config
- [ ] Route `/oauth/callback` exists (already in `app.py`)
- [ ] Test OAuth login after deployment

---

## 🔍 How to Verify It's Working

1. **Check callback URL in logs:**
   - When you click "Login with Wikimedia" on Toolforge
   - Check Flask logs for: `Using OAuth callback URL: https://wikicontest.toolforge.org/oauth/callback`
   - Should match your OAuth consumer registration

2. **Test OAuth flow:**
   - Go to: https://wikicontest.toolforge.org
   - Click "Login with Wikimedia"
   - Should redirect to Wikimedia, then back to Toolforge
   - Should log you in successfully

---

## 🆘 Troubleshooting

### Error: "oauth_callback must be set to oob"
- **Cause:** `OAUTH_CALLBACK_PATH` not set in config
- **Fix:** Add `OAUTH_CALLBACK_PATH = "/oauth/callback"` to `config.toml`

### Error: "Invalid redirect URI"
- **Cause:** Callback URL doesn't match consumer registration
- **Fix:** Verify consumer callback is: `https://wikicontest.toolforge.org/oauth/callback`

### Error: "OAuth session expired"
- **Cause:** Session cookies not persisting (same as localhost issue)
- **Fix:** The cache fallback should handle this, but check session config

---

## 📚 Summary

**For Local Development:**
- Use local consumer: `ff02bad2706bef15385eec1471ee03ea`
- Don't set `OAUTH_CALLBACK_PATH` (uses default)
- Callback: `http://localhost:5000/api/user/oauth/callback`

**For Toolforge Production:**
- Use Toolforge consumer: `3f383c834a07a181723f1a1de566f7cf`
- Set `OAUTH_CALLBACK_PATH = "/oauth/callback"`
- Callback: `https://wikicontest.toolforge.org/oauth/callback`

**No code changes needed!** Just update the configuration file. 🎉

