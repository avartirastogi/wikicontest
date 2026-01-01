# WikiContest Platform

A comprehensive web platform for hosting and managing collaborative Wikipedia article competitions. Built with Flask (Python) backend and Vue.js 3 frontend.

## Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [OAuth Setup](#oauth-setup)
- [Testing](#testing)
- [Production Deployment](#production-deployment)
- [Project Structure](#project-structure)
- [Frontend Technology](#frontend-technology)
- [Contributing](#contributing)

---

## Overview

### What This App Does

- **User Authentication** - Register, login, and manage user accounts with support for email/password and OAuth
- **Contest Management** - Create contests, set dates, define rules, and assign jury members
- **Article Submissions** - Submit Wikipedia articles to contests and track their progress
- **Dashboard & Analytics** - View user statistics, contest overview, and leaderboards
- **Responsive Design** - Optimized for desktop and mobile devices
- **Real-time Updates** - Dynamic content loading and notifications

---

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python** 3.8 or higher
- **MySQL** 8.0 or higher (or use SQLite for quick testing)
- **Node.js** 16+ (for frontend development)

---

## Quick Start

Follow these steps to get the WikiContest platform running locally:

### 1. Clone the Repository

```bash
git clone <repository-url>
cd wikicontest/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# On macOS/Linux
source venv/bin/activate

# On Windows
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Setup MySQL Database

**Option A: MySQL (Recommended for Production)**

```bash
# Connect to MySQL
mysql -u root -p

# Create database
CREATE DATABASE wikicontest;
```

**Option B: SQLite (Quick Testing)**

Skip MySQL setup and use SQLite by editing `.env` (step 5) to use:
```env
DATABASE_URL=sqlite:///wikicontest.db
```

### 5. Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env and update your configuration
# At minimum, update DATABASE_URL with your MySQL credentials
```

**Example `.env` configuration:**
```env
DATABASE_URL=mysql+pymysql://root:password@localhost/wikicontest
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here
```

### 6. Initialize Database

The application uses **Alembic** for database migrations. Run migrations to create the database schema:

```bash
# Apply all migrations
alembic upgrade head

# Alternative: Use helper script
python scripts/migrate.py upgrade head
```

**Important:** The app does not automatically run migrations on startup. You must run Alembic migrations manually before starting the application.

### 7. Run the Application

You have two options for running the application:

#### Option A: Development Mode (Recommended)

Run both Flask and Vue.js dev servers in separate terminals for the best development experience:

**Terminal 1 - Flask Backend:**
```bash
python main.py
```

**Terminal 2 - Vue.js Frontend:**
```bash
cd ../frontend
npm install  # Only needed first time
npm run dev
```

**Access at:** `http://localhost:5173` (Vue.js dev server proxies API requests to Flask)

#### Option B: Production Build (Single Server)

Build the Vue.js frontend first, then run Flask to serve both API and built frontend:

```bash
# Build frontend
cd ../frontend
npm install  # Only needed first time
npm run build

# Run Flask
cd ../backend
python main.py
```

**Access at:** `http://localhost:5000` (Flask serves built Vue.js files)

### 8. Open in Browser

- **Development Mode:** `http://localhost:5173`
- **Production Build:** `http://localhost:5000`

You should see the WikiContest login page. Register a new account to get started!

---

## Configuration

### Environment Variables

The `.env.example` file contains all available configuration options. Copy it to `.env` and customize:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://username:password@localhost/wikicontest

# Security Keys (CHANGE IN PRODUCTION!)
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# CORS Configuration (for frontend development)
CORS_ORIGINS=http://localhost:5173,http://localhost:5000

# OAuth 1.0a (Optional - for Wikimedia login)
OAUTH_MWURI=https://meta.wikimedia.org/w/index.php
CONSUMER_KEY=your-consumer-key-here
CONSUMER_SECRET=your-consumer-secret-here
```

### Configuration Tips

- **Database**: Use MySQL for production, SQLite for quick local testing
- **Security Keys**: Generate strong random keys for production environments
- **CORS**: Add your frontend URLs to allow cross-origin requests during development
- **OAuth**: Optional feature for Wikimedia login (see [OAuth Setup](#oauth-setup))

---

## Running the Application

### Development Workflow

For the best development experience:

1. **Run Flask backend** in one terminal: `python main.py`
2. **Run Vue.js dev server** in another terminal: `cd ../frontend && npm run dev`
3. **Access** the app at `http://localhost:5173`

The Vue.js dev server provides:
- Hot module replacement (instant updates)
- Automatic API proxying to Flask
- Better debugging experience

### Production Workflow

For production or testing the production build:

1. **Build frontend**: `cd frontend && npm run build`
2. **Run Flask**: `cd backend && python main.py`
3. **Access** the app at `http://localhost:5000`

Flask serves the optimized, built Vue.js files.
## 🔧 Configuration

The `.env.example` file contains all configuration options. Copy it to `.env` and update:

- **Database**: MySQL connection string (default)
- **Security Keys**: Change in production!
- **CORS**: Frontend development URLs
- **OAuth 1.0a**: Wikimedia OAuth credentials (optional, for OAuth login)


### Important Notes

- **Migrations**: Always run `alembic upgrade head` before starting the app
- **Frontend Development**: Use the Vue.js dev server (`npm run dev`) for the best experience
- **API Access**: Backend API is available at `http://localhost:5000/api/`

---

## OAuth Setup

### OAuth 1.0a for Wikimedia Login (Optional)

Enable users to log in using their Wikimedia accounts:

### 1. Register OAuth Consumer

1. Go to [Wikimedia OAuth Registration](https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration)
2. Fill in your application details
3. Set the callback URL:
   - **Development:** `http://localhost:5000/api/user/oauth/callback`
   - **Production:** `https://yourdomain.com/api/user/oauth/callback`
4. Save and note your **Consumer Key** and **Consumer Secret**

### 2. Add Credentials to `.env`

```env
OAUTH_MWURI=https://meta.wikimedia.org/w/index.php
CONSUMER_KEY=your-consumer-key-from-registration
CONSUMER_SECRET=your-consumer-secret-from-registration
```

### 3. Test OAuth Login

1. Start the application
2. Navigate to the login page
3. Click **"Login with Wikimedia"**
4. Authorize the application on Wikimedia
5. You'll be redirected back and logged in automatically

**Note:** OAuth login works alongside regular email/password authentication. Users can choose either method.

---

## Testing

### Manual Testing

```bash
# Ensure migrations are applied
alembic upgrade head

# Start the application
python main.py

# Open http://localhost:5000 (or http://localhost:5173 in dev mode)
```

### Test the Following Features:

- User registration and login
- Contest creation
- Article submission
- Dashboard functionality
- Leaderboard display
- OAuth login (if configured)

### Automated Tests

```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest

# Run with coverage
pytest --cov=app tests/
```

---

## Production Deployment

### 1. Setup Production Environment

Configure production environment variables:

```bash
export FLASK_ENV=production
export FLASK_DEBUG=False
export DATABASE_URL=mysql+pymysql://user:pass@prod-host/wikicontest
export SECRET_KEY=strong-random-production-key
export JWT_SECRET_KEY=strong-random-jwt-key
```

### 2. Build Frontend

```bash
cd frontend
npm install
npm run build
```

### 3. Apply Database Migrations

```bash
cd backend
alembic upgrade head
```

### 4. Run with Production Server

```bash
# Install Gunicorn
pip install gunicorn

# Run with 4 worker processes
gunicorn -w 4 -b 0.0.0.0:5000 "app:app"
```

### 5. Use Reverse Proxy (Recommended)

Set up Nginx or Apache as a reverse proxy:

**Example Nginx configuration:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## Project Structure

```
wikicontest/
├── backend/                    # Flask backend application
│   ├── main.py                # Application entry point
│   ├── app/                   # Main application package
│   │   ├── __init__.py       # Flask app factory
│   │   ├── config.py         # Configuration management
│   │   ├── database.py       # SQLAlchemy database
│   │   ├── models/           # Database models (User, Contest, Submission)
│   │   ├── routes/           # API endpoints (blueprints)
│   │   ├── middleware/       # Authentication & authorization
│   │   └── utils/            # Utility functions
│   ├── alembic/              # Database migrations (Alembic)
│   │   ├── versions/         # Migration version files
│   │   └── env.py            # Alembic environment
│   ├── scripts/              # Utility scripts
│   ├── tests/                # Test files (pytest)
│   ├── requirements.txt      # Python dependencies
│   └── .env                  # Environment configuration
│
└── frontend/                  # Vue.js 3 frontend application
    ├── src/                  # Source files
    │   ├── views/           # Page components (Home, Login, Dashboard, etc.)
    │   ├── components/      # Reusable UI components
    │   ├── router/          # Vue Router configuration
    │   ├── store/           # State management (if using Vuex/Pinia)
    │   ├── services/        # API service layer
    │   └── App.vue          # Root component
    ├── public/              # Static assets
    ├── package.json         # Frontend dependencies
    ├── vite.config.js       # Vite build configuration
    └── index.html           # HTML entry point
```

### Key Directories

- **`backend/app/models/`** - Database models (User, Contest, Submission)
- **`backend/app/routes/`** - API endpoints organized by domain
- **`backend/alembic/versions/`** - Database migration history
- **`frontend/src/views/`** - Vue page components
- **`frontend/src/components/`** - Reusable Vue components

---

## Frontend Technology

The frontend is built with modern Vue.js 3 and related technologies:

### Tech Stack

- **Vue.js 3** - Progressive JavaScript framework with Composition API
- **Vue Router** - Official router for client-side navigation
- **Vite** - Next-generation frontend tooling for fast development
- **Bootstrap 5** - CSS framework for responsive design
- **Axios** - Promise-based HTTP client for API communication

### Frontend Features

- Component-based architecture
- Reactive data binding
- Client-side routing
- State management
- Hot module replacement in development
- Optimized production builds

### Frontend Setup

For detailed frontend setup instructions, see [`docs/VUE_FRONTEND_SETUP.md`](docs/VUE_FRONTEND_SETUP.md).

**Quick frontend commands:**
```bash
cd frontend

# Install dependencies
npm install

# Development server with HMR
npm run dev

# Production build
npm run build

# Preview production build
npm run preview
```

---

## Contributing

We welcome contributions to the WikiContest platform!

### How to Contribute

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
   - Follow existing code style
   - Add tests for new features
   - Update documentation as needed
4. **Test thoroughly**
   - Test both backend and frontend
   - Ensure all tests pass
5. **Submit a pull request**
   - Describe your changes clearly
   - Reference any related issues

### Development Guidelines

- Follow Python PEP 8 for backend code
- Follow Vue.js style guide for frontend code
- Write meaningful commit messages
- Add docstrings to Python functions
- Comment complex logic
- Keep functions focused and under 50 lines when possible

---

## Additional Resources

- **Backend Documentation:** [`backend/README.md`](backend/README.md)
- **Frontend Setup Guide:** [`docs/VUE_FRONTEND_SETUP.md`](docs/VUE_FRONTEND_SETUP.md)
- **Database Migrations:** [`docs/ALEMBIC_USAGE_GUIDE.md`](docs/ALEMBIC_USAGE_GUIDE.md)
- **API Documentation:** See backend README for complete endpoint list

---

## License

This project is part of the WikiContest platform.

---

**WikiContest Platform** - Empowering collaborative Wikipedia article competitions! 