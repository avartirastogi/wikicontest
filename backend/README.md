# WikiContest Flask Backend

A Python Flask backend application for the WikiContest platform, converted from Node.js/Express to Python/Flask with SQLAlchemy ORM and MySQL database.

## Features

- **User Management**: Registration, login, logout, profile management
- **Contest Management**: Create, view, and manage contests
- **Submission System**: Submit articles to contests, review submissions
- **Role-Based Access Control**: Admin, creator, jury, and participant roles
- **JWT Authentication**: Secure token-based authentication
- **MySQL Database**: Robust database with SQLAlchemy ORM
- **RESTful API**: Clean API endpoints for frontend integration

## Project Structure

```
backend_python/
├── app.py                 # Main Flask application
├── requirements.txt       # Python dependencies
├── init_db.py           # Database initialization script
├── .env.example         # Environment configuration template
├── models/              # SQLAlchemy models
│   ├── user.py         # User model
│   ├── contest.py      # Contest model
│   └── submission.py   # Submission model
├── routes/              # API routes
│   ├── user_routes.py  # User management routes
│   ├── contest_routes.py # Contest management routes
│   └── submission_routes.py # Submission management routes
└── middleware/          # Authentication middleware
    └── auth.py         # JWT and permission handling
```

## Prerequisites

- Python 3.8 or higher
- MySQL 5.7 or higher
- pip (Python package manager)

## Installation

1. **Clone or navigate to the backend directory:**
   ```bash
   cd backend_python
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up MySQL database:**
   ```sql
   CREATE DATABASE wikicontest;
   CREATE USER 'wikicontest_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON wikicontest.* TO 'wikicontest_user'@'localhost';
   FLUSH PRIVILEGES;
   ```

5. **Configure environment variables:**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` file with your database credentials:
   ```
   DATABASE_URL=mysql+pymysql://wikicontest_user:your_password@localhost/wikicontest
   SECRET_KEY=your_secret_key_here
   JWT_SECRET_KEY=your_jwt_secret_key_here
   ```

6. **Initialize the database:**
   ```bash
   # Create tables only
   python init_db.py
   
   # Create tables with sample data
   python init_db.py seed
   
   # Reset database (drops all tables and recreates)
   python init_db.py reset
   ```

## Running the Application

1. **Start the Flask development server:**
   ```bash
   python app.py
   ```

2. **The API will be available at:**
   - Base URL: `http://localhost:5000`
   - API endpoints: `http://localhost:5000/api/`

## API Endpoints

### User Management
- `POST /api/user/register` - Register a new user
- `POST /api/user/login` - Login user
- `POST /api/user/logout` - Logout user
- `GET /api/user/dashboard` - Get user dashboard
- `GET /api/user/all` - Get all users (admin only)
- `GET /api/user/profile` - Get user profile
- `PUT /api/user/profile` - Update user profile

### Contest Management
- `GET /api/contest` - Get all contests
- `POST /api/contest` - Create a new contest
- `GET /api/contest/<id>` - Get contest by ID
- `DELETE /api/contest/<id>` - Delete contest
- `GET /api/contest/<id>/leaderboard` - Get contest leaderboard
- `POST /api/contest/<id>/submit` - Submit to contest
- `GET /api/contest/<id>/submissions` - Get contest submissions

### Submission Management
- `GET /api/submission` - Get all submissions (admin only)
- `GET /api/submission/<id>` - Get submission by ID
- `PUT /api/submission/<id>` - Update submission status
- `GET /api/submission/user/<user_id>` - Get user submissions
- `GET /api/submission/contest/<contest_id>` - Get contest submissions
- `GET /api/submission/pending` - Get pending submissions
- `GET /api/submission/stats` - Get submission statistics

### Utility Endpoints
- `GET /api/cookie` - Check authentication status
- `GET /api/health` - Health check

## Database Models

### User Model
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `role`: User role (admin, user)
- `password`: Hashed password
- `score`: Total accumulated score
- `created_at`: Creation timestamp

### Contest Model
- `id`: Primary key
- `name`: Contest name
- `project_name`: Associated project name
- `created_by`: Creator username (foreign key)
- `description`: Contest description
- `start_date`: Contest start date
- `end_date`: Contest end date
- `rules`: JSON rules object
- `marks_setting_accepted`: Points for accepted submissions
- `marks_setting_rejected`: Points for rejected submissions
- `jury_members`: Comma-separated jury usernames
- `created_at`: Creation timestamp

### Submission Model
- `id`: Primary key
- `user_id`: User ID (foreign key)
- `contest_id`: Contest ID (foreign key)
- `article_title`: Article title
- `article_link`: Article URL
- `status`: Submission status (pending, accepted, rejected)
- `score`: Awarded score
- `submitted_at`: Submission timestamp

## Authentication & Authorization

The application uses JWT (JSON Web Tokens) for authentication with the following features:

- **JWT Tokens**: Stored in HTTP-only cookies for security
- **Role-Based Access**: Admin, creator, jury, and participant roles
- **Permission System**: Contextual permissions based on contest relationships
- **Middleware**: Automatic authentication and authorization checks

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-flask

# Run tests
pytest
```

### Code Style
The code follows Python PEP 8 standards with comprehensive comments and documentation.

### Database Migrations
For production deployments, consider using Flask-Migrate for database schema versioning.

## Production Deployment

1. **Set production environment variables:**
   ```
   FLASK_ENV=production
   FLASK_DEBUG=False
   DATABASE_URL=mysql+pymysql://user:pass@host:port/db
   ```

2. **Use a production WSGI server:**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

3. **Set up reverse proxy with Nginx:**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;
       
       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Error:**
   - Check MySQL service is running
   - Verify database credentials in `.env`
   - Ensure database exists

2. **Import Errors:**
   - Activate virtual environment
   - Install all dependencies: `pip install -r requirements.txt`

3. **JWT Token Issues:**
   - Check `JWT_SECRET_KEY` in environment variables
   - Ensure cookies are enabled in frontend

4. **Permission Errors:**
   - Verify user roles in database
   - Check contest relationships for contextual permissions

### Logs
Application logs are written to console by default. For production, configure proper logging in `app.py`.

## Contributing

1. Follow PEP 8 style guidelines
2. Add comprehensive comments and docstrings
3. Write tests for new features
4. Update documentation for API changes

## License

This project is part of the WikiContest platform.
