# WikiContest Platform

A web platform for hosting and participating in collaborative online competitions. Built with Flask (Python) backend and vanilla JavaScript frontend.

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
   source venv/bin/activate  # On Windows: venv\Scripts\activate
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

6. **Initialize database**
   ```bash
   python init_db.py
   ```

7. **Run the application**
   ```bash
   python app.py
   ```

8. **Open in browser**
   ```
   http://localhost:5000
   ```

**Quick Testing Option**: If you want to skip MySQL setup, edit `.env` and change `DATABASE_URL` to `sqlite:///wikicontest.db`

## 🔧 Configuration

The `.env.example` file contains all configuration options. Copy it to `.env` and update:

- **Database**: MySQL connection string (default)
- **Security Keys**: Change in production!
- **CORS**: Frontend development URLs

## 🧪 Testing

```bash
# Test the application
python app.py
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

2. **Run with production server**
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

## Project Structure

```
wikicontest/
├── backend/           # Flask application
│   ├── app.py        # Main application
│   ├── models/       # Database models
│   ├── routes/        # API endpoints
│   └── middleware/    # Authentication
└── frontend/         # Frontend files
    ├── index.html    # Main page
    └── app.js        # JavaScript
```

##  Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

---

**WikiContest Platform** - Ready for collaborative online competitions! 