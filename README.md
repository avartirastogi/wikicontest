# WikiContest Platform

A web platform for hosting and participating in collaborative online competitions. Built with Flask (Python) backend and Vue.js 3 frontend.

##  What This App Does

- **User Authentication**: Register, login, and manage user accounts
- **Contest Management**: Create contests, set dates, assign jury members
- **Dashboard**: View user statistics and contest overview
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Updates**: Dynamic content loading and notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MySQL 8.0+ (or use SQLite for quick testing)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd wikicontest/backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: source venv/Scripts/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup MySQL database**
   ```bash
   # Create database in MySQL
   mysql -u root -p
   CREATE DATABASE wikicontest;
   ```

5. **Setup environment**
   ```bash
   cp .env.example .env
   # Edit .env and update your MySQL credentials
   ```

6. **Setup OAuth (Optional - for Wikimedia login)**
   
   To enable OAuth 1.0a login with Wikimedia:
   
   a. Register an OAuth consumer at: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration
   
   b. Set the callback URL to: `http://localhost:5000/api/user/oauth/callback` (or your production URL)
   
   c. Add your OAuth credentials to `.env`:
   ```env
   OAUTH_MWURI=https://meta.wikimedia.org/w/index.php
   CONSUMER_KEY=your-consumer-key-here
   CONSUMER_SECRET=your-consumer-secret-here
   ```
   
   d. Users can then click "Login with Wikimedia" on the login page

7. **Initialize database with Alembic migrations**
   ```bash
   # Apply all database migrations
   alembic upgrade head
   
   # Or use the helper script
   python scripts/migrate.py upgrade head
   ```
   
   **Note**: The app does not automatically run migrations on startup. You must run Alembic migrations manually before starting the application.

8. **Run the application**

   **Option A: Development Mode (Recommended)**
   
   Run both servers in separate terminals:
   
   Terminal 1 - Flask Backend:
   ```bash
   python main.py
   ```
   
   Terminal 2 - Vue.js Frontend:
   ```bash
   cd ../frontend
   npm install  # Only needed first time
   npm run dev
   ```
   
   Access at: `http://localhost:5173` (Vue.js dev server proxies API to Flask)
   
   **Option B: Production Build (Single Server)**
   
   Build Vue.js first, then run Flask:
   ```bash
   cd ../frontend
   npm install  # Only needed first time
   npm run build
   cd ../backend
   python main.py
   ```
   
   Access at: `http://localhost:5000` (Flask serves built Vue.js files)

9. **Open in browser**
   - Development: `http://localhost:5173` (with Vue.js dev server)
   - Production: `http://localhost:5000` (Flask serves built files)

**Quick Testing Option**: If you want to skip MySQL setup, edit `.env` and change `DATABASE_URL` to `sqlite:///wikicontest.db`

**Database Migrations**: The application uses Alembic for database migrations. Always run `alembic upgrade head` before starting the app to ensure your database schema is up to date. The app does not automatically run migrations on startup.

**Frontend Development**: For the best development experience, run the Vue.js dev server (`npm run dev` in `frontend/` directory) alongside Flask. The dev server proxies API requests to Flask automatically.

## 🔧 Configuration

The `.env.example` file contains all configuration options. Copy it to `.env` and update:

- **Database**: MySQL connection string (default)
- **Security Keys**: Change in production!
- **CORS**: Frontend development URLs
- **OAuth 1.0a**: Wikimedia OAuth credentials (optional, for OAuth login)

### OAuth 1.0a Setup (for Wikimedia Login)

1. **Register OAuth Consumer**:
   - Go to: https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration
   - Fill in your application details
   - Set callback URL: `http://localhost:5000/api/user/oauth/callback` (development)
   - For production, use your production URL: `https://yourdomain.com/api/user/oauth/callback`

2. **Add Credentials to `.env`**:
   ```env
   OAUTH_MWURI=https://meta.wikimedia.org/w/index.php
   CONSUMER_KEY=your-consumer-key-from-registration
   CONSUMER_SECRET=your-consumer-secret-from-registration
   ```

3. **Test OAuth Login**:
   - Start the application
   - Click "Login with Wikimedia" on the login page
   - Authorize the application on Wikimedia
   - You'll be redirected back and logged in

**Note**: OAuth login works alongside regular email/password login. Users can choose either method.

## 🧪 Testing

```bash
# Make sure migrations are applied first
alembic upgrade head

# Test the application
python main.py
# Open http://localhost:5000 and test:
# - User registration/login
# - Contest creation
# - Dashboard functionality
```

## 🚀 Production Deployment

1. **Setup production environment**
   ```bash
   export FLASK_ENV=production
   export DATABASE_URL=your-production-mysql-url
   ```

2. **Apply database migrations**
   ```bash
   alembic upgrade head
   ```

3. **Run with production server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 "app:app"
   ```

## Project Structure

```
wikicontest/
├── backend/           # Flask application
│   ├── main.py       # Application entry point
│   ├── app/          # Application package
│   │   ├── __init__.py  # Flask app factory
│   │   ├── models/   # Database models
│   │   ├── routes/   # API endpoints
│   │   └── middleware/ # Authentication
│   ├── alembic/      # Database migrations (Alembic)
│   └── scripts/      # Utility scripts
└── frontend/         # Vue.js frontend
    ├── src/          # Source files
    │   ├── views/    # Page components
    │   ├── components/ # Reusable components
    │   ├── router/   # Vue Router
    │   ├── store/    # State management
    │   └── services/ # API service
    ├── package.json  # Dependencies
    └── vite.config.js # Build configuration
```

## Frontend Technology

The frontend uses **Vue.js 3** with:
- Vue Router for client-side routing
- Vite for fast development and optimized builds
- Bootstrap 5 for styling
- Axios for API communication

See `docs/VUE_FRONTEND_SETUP.md` for frontend setup instructions.

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**WikiContest Platform** - Ready for collaborative online competitions! 