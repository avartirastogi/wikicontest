# WikiContest Project Documentation

## 📋 Project Overview

**WikiContest** is a web-based platform designed to organize and manage Wikipedia editing contests (Edit-a-thons). It allows users to create contests, submit edits, track progress, and compete in leaderboards while maintaining proper authentication and role-based access control.

### 🎯 What This Project Does

1. **Contest Management**: Create, manage, and participate in Wikipedia editing contests
2. **User Authentication**: Secure login/logout with JWT tokens and role-based access
3. **Submission Tracking**: Submit and review Wikipedia edits for contests
4. **Leaderboards**: Real-time ranking of participants based on edit quality and quantity
5. **Admin Controls**: Contest creators can manage submissions and scores
6. **Toolforge Integration**: Deployable on Wikimedia's Toolforge platform with OAuth authentication

## 🏗️ Project Architecture

### Technology Stack

- **Backend**: Python Flask (application factory) with SQLAlchemy ORM
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla JS)
- **Database**: MySQL (default). SQLite optional for quick testing
- **Authentication**: JWT in HTTP-only cookies + CSRF via `X-CSRF-TOKEN` header; OAuth 1.0a for Toolforge
- **Deployment**: Local dev (Flask) and Toolforge (Wikimedia)

### File Structure (Updated)

```
wikicontest/
├── backend/                        # Flask backend application
│   ├── models/                    # SQLAlchemy ORM models
│   │   ├── user.py               # User model and database operations
│   │   ├── contest.py            # Contest model and database operations
│   │   └── submission.py         # Submission model and database operations
│   ├── routes/                   # API route handlers
│   │   ├── user_routes.py        # User-related API endpoints
│   │   ├── contest_routes.py     # Contest-related API endpoints
│   │   └── submission_routes.py  # Submission-related API endpoints
│   ├── middleware/               # Authentication and authorization
│   │   └── auth.py              # JWT middleware and role-based access
│   ├── app.py                   # App factory + blueprint registration + error handlers
│   ├── config.py                # Centralized configuration (development/testing/production)
│   ├── utils.py                 # Reusable helpers (responses, validation, pagination)
│   ├── database.py              # SQLAlchemy DB initialization
│   ├── requirements.txt         # Python dependencies
│   ├── init_db.py               # Database initialization script
│   ├── setup.py                 # Environment setup helper
│   ├── toolforge_app.py         # Toolforge-specific Flask application
│   ├── toolforge_config.toml    # Toolforge configuration
│   ├── toolforge_requirements.txt # Toolforge dependencies
│   ├── deploy_to_toolforge.sh   # Toolforge deployment script
│   └── TOOLFORGE_DEPLOYMENT.md  # Toolforge deployment guide
├── frontend/                    # Frontend application
│   ├── index.html              # Main HTML page
│   └── app.js                  # Frontend JavaScript logic
└── README.md                   # Quick start and setup
```

## 🗄️ Database Configuration

### **Local Development**
- **Database (default)**: MySQL (recommended)
- **Alternative**: SQLite for quick local testing
- **Configuration**:
  - Set `DATABASE_URL` in `.env` (MySQL default):
    - `mysql+pymysql://<user>:<pass>@localhost/wikicontest`
  - For SQLite quick test:
    - `sqlite:///wikicontest.db`

### **Toolforge Production**
- **Database**: **MySQL** (Recommended by Toolforge)
- **Host**: `tools-db` (Toolforge's MySQL server)
- **Purpose**: Production-grade performance and reliability
- **Configuration**: `SQLALCHEMY_DATABASE_URI = "mysql://username:password@tools-db/database_name"`

## 🗄️ Database Schema (ORM Models)

### User Model (`backend/models/user.py`)
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), default='user')  # 'user', 'admin'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Purpose**: Manages user accounts, authentication, and role-based permissions.

### Contest Model (`backend/models/contest.py`)
```python
class Contest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Purpose**: Manages contest information, timing, and creator relationships.

### Submission Model (`backend/models/submission.py`)
```python
class Submission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contest_id = db.Column(db.Integer, db.ForeignKey('contest.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    article_title = db.Column(db.String(200), nullable=False)
    edit_summary = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'approved', 'rejected'
    score = db.Column(db.Integer, default=0)
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**Purpose**: Tracks user submissions, scores, and approval status for each contest.

## 🔧 Backend Architecture

### Main Application Files

#### `backend/app.py` - Application Factory Entrypoint
- **Purpose**: Creates and configures the Flask app (factory pattern)
- **Features**:
  - Centralized config via `config.py`
  - SQLAlchemy initialization
  - JWT-in-cookies with CSRF protection
  - CORS configuration
  - Blueprint registration (`user`, `contest`, `submission`)
  - Health checks and error handlers

#### `backend/toolforge_app.py` - Toolforge Production Server
- **Purpose**: Toolforge-specific Flask application
- **Features**:
  - OAuth 1.0a authentication with Wikimedia
  - Configuration loading from TOML files
  - Toolforge-specific routing
  - Jinja2 template rendering
  - Production-ready error handling

### API Routes

Base URL prefix: `/api`

#### User Routes (`backend/routes/user_routes.py`)
- `POST /api/user/register` (public)
  - Body: `{ username, email, password, role? }`
  - Returns 201 with `{ message, userId, username }`
- `POST /api/user/login` (public)
  - Body: `{ email, password }`
  - Returns 200 with `{ message, userId, username }` and sets JWT cookie
- `POST /api/user/logout` (auth + CSRF)
  - Clears JWT cookies; returns `{ message }`
- `GET /api/user/dashboard` (auth)
  - Returns user dashboard data: totals, per-contest scores, submissions, created and jury contests
- `GET /api/user/all` (admin)
  - Returns list of all users
- `GET /api/user/profile` (auth)
  - Returns current user profile
- `PUT /api/user/profile` (auth)
  - Body: `{ username, email }`
  - Updates profile; returns `{ message }`

#### Contest Routes (`backend/routes/contest_routes.py`)
- `GET /api/contest/` (public)
  - Returns `{ current, upcoming, past }` contests
- `POST /api/contest/` (auth)
  - Body (required): `{ name, project_name, jury_members: string[] }`
  - Body (optional): `{ code_link, description, start_date, end_date, rules, marks_setting_accepted, marks_setting_rejected }`
  - Returns 201 with `{ message, contestId }`
- `GET /api/contest/<id>` (public)
  - Returns contest details
- `GET /api/contest/<id>/leaderboard` (public)
  - Returns leaderboard for contest
- `DELETE /api/contest/<id>` (auth: admin or creator)
  - Deletes contest and its submissions; returns `{ message }`
- `POST /api/contest/<id>/submit` (auth)
  - Body: `{ article_title, article_link }`
  - Returns 201 with `{ message, submissionId, contest_id, article_title }`
- `GET /api/contest/<id>/submissions` (auth: admin, jury, or creator)
  - Returns list of submissions for contest

#### Submission Routes (`backend/routes/submission_routes.py`)
- `GET /api/submission/` (auth: admin)
  - Returns list of all submissions
- `GET /api/submission/<id>` (permission: can view)
  - Returns submission details (includes user info)
- `PUT /api/submission/<id>` (permission: jury or admin)
  - Body: `{ status: 'accepted' | 'rejected' }`
  - Updates status and recalculates score; returns `{ message, status, score }`
- `GET /api/submission/user/<user_id>` (auth: self or admin)
  - Returns submissions for a specific user
- `GET /api/submission/contest/<contest_id>` (auth: admin, jury, or creator)
  - Returns submissions for a specific contest
- `GET /api/submission/pending` (auth)
  - Returns submissions the current user can judge
- `GET /api/submission/stats` (auth)
  - Returns submission statistics for current user

#### Misc
- `GET /api/cookie` (auth via cookie)
  - Returns current authenticated user info `{ userId, username, email }`

Notes:
- Authentication uses JWT stored in HTTP-only cookies.
- CSRF: Send `X-CSRF-TOKEN` header with the value from `csrf_access_token` cookie for state-changing requests (e.g., logout, POST/PUT/DELETE).

### Authentication Middleware (`backend/middleware/auth.py`)
- **JWT Token Verification**: Validates user tokens
- **Role-Based Access Control**: Enforces user/admin permissions
- **User Context**: Provides current user information to routes
- **Cookies + CSRF**: JWT stored in HTTP-only cookies; CSRF expected in `X-CSRF-TOKEN` header

## 🎨 Frontend Architecture

### `frontend/index.html`
- **Purpose**: Main HTML structure and UI components
- **Features**:
  - Responsive design with CSS Grid/Flexbox
  - Modal dialogs for forms
  - Dynamic content loading
  - User authentication UI
  - Contest management interface
  - Leaderboard display

### `frontend/app.js`
- **Purpose**: Frontend JavaScript logic and API communication
- **Features**:
  - API client for backend communication
  - User authentication management
  - Contest creation and participation
  - Real-time UI updates
  - Form validation and submission
  - Error handling and user feedback

## 🚀 Deployment Options

### Local Development
1. **Backend**: `cd backend && python app.py`
2. **Frontend**: Served by Flask at `http://localhost:5000`
3. **Database**: MySQL (default) or SQLite if configured

### Toolforge Production
1. **Backend**: `python backend/toolforge_app.py`
2. **Frontend**: Served by Flask with Jinja2 templates
3. **Database**: **MySQL on Toolforge** (Recommended for production)
4. **Authentication**: OAuth 1.0a with Wikimedia accounts
5. **URL**: `https://wikicontest.toolforge.org`

## 🔐 Security Features

1. **JWT Authentication**: Secure token-based authentication
2. **Password Hashing**: bcrypt for secure password storage
3. **Role-Based Access**: User/Admin permission system
4. **CORS Protection**: Cross-origin request security
5. **OAuth Integration**: Wikimedia account authentication
6. **Input Validation**: Server-side validation for all inputs

## 📊 Key Features

### For Regular Users
- Register and login to the platform
- View available contests
- Submit Wikipedia edits for contests
- Track submission status and scores
- View leaderboards and rankings

### For Contest Creators
- Create new editing contests
- Set contest parameters (title, description, dates)
- Review and score submissions
- Manage contest participants
- View detailed analytics

### For Administrators
- Manage all users and contests
- Review all submissions
- Update scores and statuses
- Access system-wide analytics

## 🛠️ Development Workflow

1. **Setup**: Run `python backend/setup.py` to initialize environment
2. **Database**: Run `python backend/init_db.py` to create tables
3. **Testing**: Run `python backend/test_app.py` to verify functionality
4. **Development**: Use `python backend/app.py` for local development
5. **Deployment**: Use `bash backend/deploy_to_toolforge.sh` for Toolforge

## 📈 Future Enhancements

- Real-time notifications
- Advanced analytics and reporting
- Integration with Wikipedia API
- Mobile-responsive improvements
- Automated scoring algorithms
- Contest templates and presets

## 🔗 External Integrations

- **Wikimedia OAuth**: User authentication via Wikimedia accounts
- **Wikipedia API**: Potential integration for edit validation
- **Toolforge Platform**: Hosting and deployment infrastructure
- **MySQL Database**: Production database on Toolforge (Recommended)
- **SQLite Database**: Local development database

This project provides a complete solution for organizing Wikipedia editing contests with proper authentication, user management, and contest tracking capabilities.
