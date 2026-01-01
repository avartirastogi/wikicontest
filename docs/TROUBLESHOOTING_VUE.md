# Troubleshooting Vue.js Frontend Issues

This guide helps you diagnose and resolve common issues when running the Vue.js frontend with the Flask backend.

---

## Login Buttons Not Showing

If login/register buttons are missing on `http://localhost:5173`, follow these steps:

### 1. Check Browser Console for Errors

Open your browser's DevTools (`F12`) and navigate to the **Console** tab. Look for any JavaScript errors or warnings that might indicate what's failing.

### 2. Inspect Network Requests

Check if API calls to `/api/cookie` are functioning correctly:

1. Open the **Network** tab in DevTools
2. Look for requests to `/api/cookie`
3. Verify the response status:
   - `200` = Success
   - `401` = Unauthorized (expected if not logged in)

### 3. Verify Flask Backend is Running

Ensure the Flask server is running on `http://localhost:5000`:
```bash
cd backend
python app.py
```

Check the terminal output to confirm the server started without errors.

### 4. Verify Vue.js Dev Server is Running

Ensure the Vue.js development server is active:
```bash
cd frontend
npm run dev
```

Confirm it's serving on `http://localhost:5173`.

### 5. Check CORS Configuration

Verify that Flask allows requests from the Vue.js dev server:

- Open `backend/app.py`
- Confirm `'http://localhost:5173'` is included in the CORS origins list

---

## OAuth Callback Not Working

The OAuth callback URL is fixed at `http://localhost:5000/api/user/oauth/callback` and cannot be changed.

### OAuth Authentication Flow

1. User clicks **"Login with Wikimedia"** on the Vue.js app (`localhost:5173`)
2. Request is sent to `http://localhost:5000/api/user/oauth/login`
3. Flask redirects the user to **Wikimedia** for authentication
4. After authentication, Wikimedia redirects back to `http://localhost:5000/api/user/oauth/callback`
5. Flask processes the OAuth response and redirects to the Vue.js app with `?oauth_success=true`
6. Vue.js detects the success parameter and updates the authentication state

### Troubleshooting OAuth Failures

If the OAuth redirect is not working:

1. **Check Flask logs** for OAuth-related error messages
2. **Verify OAuth consumer registration** on Wikimedia with the callback URL: `http://localhost:5000/api/user/oauth/callback`
3. **Check browser console** for redirect errors or blocked requests
4. **Verify cookies are being set** by checking the **Application** tab in DevTools (look under Cookies → `localhost`)

---

## API Requests Failing

### Check Proxy Configuration

The Vite dev server should proxy `/api` requests to Flask. Verify your `frontend/vite.config.js` contains:
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

### Test API Endpoints Directly

Verify both direct and proxied API access:

- **Direct Flask API:** `http://localhost:5000/api/health` → Should return JSON
- **Proxied through Vite:** `http://localhost:5173/api/health` → Should proxy to Flask and return JSON

If the direct endpoint works but the proxied one doesn't, the issue is with the Vite proxy configuration.

---

## Components Not Rendering

### Use Vue DevTools

Install the [Vue DevTools browser extension](https://devtools.vuejs.org/) to inspect component state, props, and events.

### Check Console for Errors

Common errors to look for:

- **Module not found errors** – Missing dependencies
- **Import errors** – Incorrect file paths or module names
- **Component registration errors** – Components not properly registered

### Reinstall Dependencies

If components are failing to load, try reinstalling dependencies:
```bash
cd frontend
npm install
```

---

## Quick Fixes

### Clear Browser Cache

- **Hard refresh:** `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)
- **Clear cookies:** Open DevTools → **Application** tab → **Cookies** → Delete cookies for `localhost`

### Restart Both Servers

1. Stop Flask backend (`Ctrl+C` in terminal)
2. Stop Vue.js dev server (`Ctrl+C` in terminal)
3. Restart both servers in their respective directories

### Rebuild Frontend Dependencies

If issues persist, try a clean reinstall:
```bash
cd frontend
rm -rf node_modules
npm install
```

---

## Still Having Issues?

If the problem persists after trying the above steps:

1. **Check the browser console** for specific error messages
2. **Check the Flask terminal** for backend errors and stack traces
3. **Check the Vue.js terminal** for frontend build or compilation errors
4. **Verify both servers are running** on the correct ports:
   - Flask: `http://localhost:5000`
   - Vue.js: `http://localhost:5173`

Collect any error messages from all three sources (browser, Flask, Vue.js) to help diagnose the root cause.