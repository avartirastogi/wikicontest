# Troubleshooting Vue.js Frontend Issues

## Issue: Login Buttons Not Showing

If you don't see login/register buttons on `http://localhost:5173`:

### Check 1: Browser Console
Open browser DevTools (F12) and check the Console tab for errors.

### Check 2: Network Tab
Check if API calls to `/api/cookie` are working:
- Open Network tab in DevTools
- Look for requests to `/api/cookie`
- Check if they return 200 or 401

### Check 3: Verify Flask is Running
Make sure Flask backend is running on `http://localhost:5000`:
```bash
cd backend
python app.py
```

### Check 4: Verify Vue.js Dev Server
Make sure Vue.js dev server is running:
```bash
cd frontend
npm run dev
```

### Check 5: Check CORS Configuration
Verify Flask CORS allows `http://localhost:5173`:
- Check `backend/app.py` - should include `'http://localhost:5173'` in CORS origins

## Issue: OAuth Callback Not Working

The OAuth callback URL `http://localhost:5000/api/user/oauth/callback` is fixed and cannot be changed.

### How It Works:

1. **User clicks "Login with Wikimedia"** on Vue.js app (`localhost:5173`)
2. **Redirects to** `http://localhost:5000/api/user/oauth/login`
3. **Flask redirects to** Wikimedia for authentication
4. **Wikimedia redirects back to** `http://localhost:5000/api/user/oauth/callback`
5. **Flask processes OAuth** and redirects to Vue.js app with `?oauth_success=true`
6. **Vue.js detects success** and updates authentication state

### If OAuth Redirect Fails:

1. **Check Flask logs** for OAuth errors
2. **Verify OAuth consumer** is registered with callback URL: `http://localhost:5000/api/user/oauth/callback`
3. **Check browser console** for redirect errors
4. **Verify cookies** are being set (check Application tab in DevTools)

## Issue: API Requests Failing

### Check Proxy Configuration

Vite dev server should proxy `/api` requests to Flask. Verify in `frontend/vite.config.js`:

```javascript
server: {
  proxy: {
    '/api': {
      target: 'http://localhost:5000',
      changeOrigin: true
    }
  }
}
```

### Test API Directly

Try accessing API directly:
- `http://localhost:5000/api/health` - Should return JSON
- `http://localhost:5173/api/health` - Should proxy to Flask and return JSON

## Issue: Components Not Rendering

### Check Vue DevTools

Install Vue DevTools browser extension to debug Vue component state.

### Check Console Errors

Look for:
- Module not found errors
- Import errors
- Component registration errors

### Verify Dependencies

```bash
cd frontend
npm install
```

## Quick Fixes

### Clear Browser Cache
- Hard refresh: `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- Clear cookies for `localhost`

### Restart Servers
1. Stop Flask (Ctrl+C)
2. Stop Vue.js dev server (Ctrl+C)
3. Restart both servers

### Rebuild Dependencies
```bash
cd frontend
rm -rf node_modules
npm install
```

## Still Having Issues?

1. **Check browser console** for specific error messages
2. **Check Flask terminal** for backend errors
3. **Check Vue.js terminal** for frontend errors
4. **Verify both servers are running** on correct ports

