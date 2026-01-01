# Frontend Comparison: Old vs New

## What Changed

### Old Frontend (Vanilla JS - served by Flask)
- **URL**: `http://localhost:5000`
- **Technology**: Vanilla JavaScript, served directly by Flask
- **Files**: `frontend/index.html` + `frontend/app.js`
- **Status**: Still exists but replaced by Vue.js

### New Frontend (Vue.js - Vite Dev Server)
- **URL**: `http://localhost:5173`
- **Technology**: Vue.js 3 with Vite
- **Files**: `frontend/src/` directory
- **Status**: Current implementation

## Key Differences

### 1. **Login Buttons**
- **Old**: Showed in navbar when not authenticated
- **New**: Same - shows Login/Register buttons when not authenticated
- **Location**: Top-right of navbar

### 2. **Login with Wikimedia**
- **Old**: Available on login page
- **New**: Available on login page (`/login` route)
- **URL**: `http://localhost:5000/api/user/oauth/login` (unchanged)

### 3. **Data Fetching**
- **Old**: Fetched from `/api/contest` endpoint
- **New**: Same - fetches from `/api/contest` endpoint
- **Method**: Both use same Flask API endpoints

### 4. **OAuth Callback**
- **Old**: Redirected to Flask URL
- **New**: Redirects to Vue.js app with `?oauth_success=true` parameter
- **Callback URL**: Still `http://localhost:5000/api/user/oauth/callback` (unchanged)

## How to Use

### Development Mode (Recommended)

1. **Start Flask Backend**:
   ```bash
   cd backend
   python app.py
   ```
   Runs on: `http://localhost:5000`

2. **Start Vue.js Frontend**:
   ```bash
   cd frontend
   npm install  # First time only
   npm run dev
   ```
   Runs on: `http://localhost:5173`

3. **Access Application**:
   - Open: `http://localhost:5173`
   - Login buttons should appear in navbar
   - Click "Login" to see "Login with Wikimedia" option

### Production Mode (Single Server)

1. **Build Vue.js**:
   ```bash
   cd frontend
   npm run build
   ```

2. **Start Flask**:
   ```bash
   cd backend
   python app.py
   ```

3. **Access Application**:
   - Open: `http://localhost:5000`
   - Flask serves built Vue.js files

## Features Comparison

| Feature | Old Frontend | New Frontend | Status |
|---------|-------------|--------------|--------|
| Login/Register buttons |  |  | Working |
| Login with Wikimedia |  |  | Working |
| Contest listing |  |  | Working |
| Dashboard |  |  | Working |
| Data fetching |  |  | Working |
| OAuth callback |  |  | Working |

## Troubleshooting

### If login buttons don't show:
1. Check browser console (F12) for errors
2. Verify Flask is running on port 5000
3. Verify Vue.js dev server is running on port 5173
4. Hard refresh browser (Ctrl+Shift+R)

### If data doesn't load:
1. Check Network tab in DevTools
2. Verify API calls to `/api/contest` are successful
3. Check Flask terminal for errors
4. Verify CORS is configured in Flask

### If OAuth doesn't work:
1. Verify OAuth consumer is registered with callback: `http://localhost:5000/api/user/oauth/callback`
2. Check Flask logs for OAuth errors
3. Verify cookies are being set (check Application tab in DevTools)

## Migration Notes

All features from the old frontend have been migrated to Vue.js:
-  User authentication
-  Contest management
-  Dashboard
-  OAuth login
-  Data fetching
-  All UI components

The Vue.js version provides:
- Better code organization
- Component-based architecture
- Better state management
- Modern development experience

