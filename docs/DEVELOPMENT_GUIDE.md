# WikiContest Development Guide

This guide provides comprehensive information for developers working on the WikiContest platform, including architecture details, coding standards, and best practices.

## 🏗️ Architecture Overview

### Backend Architecture

The backend follows a modular Flask architecture with clear separation of concerns:

```
backend/
├── app.py                 # Application factory and main entry point
├── config.py              # Environment-based configuration management
├── utils.py               # Reusable utility functions
├── database.py            # Database initialization and connection
├── models/                # SQLAlchemy data models
│   ├── user.py           # User model with authentication methods
│   ├── contest.py        # Contest model with status methods
│   └── submission.py      # Submission model for contest entries
├── routes/                # API route blueprints
│   ├── user_routes.py     # User authentication and management
│   ├── contest_routes.py  # Contest CRUD operations
│   └── submission_routes.py # Submission handling
└── middleware/            # Authentication and security middleware
    └── auth.py            # JWT authentication decorators
```

### Frontend Architecture

The frontend uses vanilla JavaScript with a modular function organization:

```javascript
// Global state management
let currentUser = null;
let currentContests = { current: [], upcoming: [], past: [] };

// Function organization by feature
// - Utility functions (showAlert, formatDate, etc.)
// - API communication functions
// - Authentication functions
// - Contest management functions
// - UI management functions
```

## 🛠️ Development Setup

### Prerequisites

- Python 3.8 or higher
- MySQL 8.0+ or PostgreSQL 12+
- Git
- Code editor (VS Code recommended)

### Local Development Environment

1. **Clone and setup**
   ```bash
   git clone <repository-url>
   cd wikicontest
   
   # Backend setup
   cd backend
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   
   # Database setup
   cp .env.example .env
   # Edit .env with your database credentials
   python init_db.py
   ```

2. **Run development server**
   ```bash
   python app.py
   ```

3. **Access application**
   - Backend API: http://localhost:5000
   - Frontend: http://localhost:5000 (served by Flask)

## 📝 Coding Standards

### Python Backend Standards

#### 1. Code Organization
- Use descriptive function and variable names
- Add comprehensive docstrings for all functions
- Group related functionality in modules
- Use type hints where appropriate

#### 2. Error Handling
```python
# Use the @handle_errors decorator for route functions
@user_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    # Function implementation
    pass

# Manual error handling for complex operations
try:
    # Operation that might fail
    result = perform_operation()
except SpecificException as e:
    return create_error_response(f"Operation failed: {str(e)}", 400)
```

#### 3. Database Operations
```python
# Use SQLAlchemy ORM methods
user = User.query.filter_by(email=email).first()
if not user:
    return create_error_response("User not found", 404)

# Use transactions for multiple operations
db.session.begin()
try:
    # Multiple database operations
    db.session.commit()
except Exception:
    db.session.rollback()
    raise
```

#### 4. API Response Format
```python
# Success responses
return create_success_response("Operation completed", data, 200)

# Error responses
return create_error_response("Error message", 400, details)
```

### JavaScript Frontend Standards

#### 1. Function Documentation
```javascript
/**
 * Brief description of the function.
 * 
 * Detailed explanation of what the function does,
 * including any important implementation details.
 * 
 * @param {string} param1 - Description of parameter
 * @param {Object} param2 - Description of parameter
 * @returns {Promise<Object>} Description of return value
 * 
 * Example:
 * const result = await functionName('value', { key: 'value' });
 */
async function functionName(param1, param2) {
    // Implementation
}
```

#### 2. Error Handling
```javascript
// Use try-catch for async operations
try {
    const result = await apiRequest('/endpoint');
    // Handle success
} catch (error) {
    showAlert(error.message, 'error');
    console.error('Operation failed:', error);
}
```

#### 3. State Management
```javascript
// Update global state consistently
currentUser = {
    id: response.userId,
    username: response.username,
    email: response.email
};

// Update UI after state changes
updateAuthUI();
```

## 🔧 Adding New Features

### Backend Feature Development

#### 1. Create a New Model
```python
# models/new_feature.py
from database import db
from datetime import datetime

class NewFeature(db.Model):
    __tablename__ = 'new_features'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'created_at': self.created_at.isoformat()
        }
```

#### 2. Create Route Blueprint
```python
# routes/new_feature_routes.py
from flask import Blueprint, request
from models.new_feature import NewFeature
from middleware.auth import require_auth
from utils import create_success_response, create_error_response

new_feature_bp = Blueprint('new_feature', __name__)

@new_feature_bp.route('/create', methods=['POST'])
@require_auth
def create_new_feature():
    """Create a new feature instance."""
    data = request.get_json()
    
    # Validation
    if not data.get('name'):
        return create_error_response('Name is required', 400)
    
    # Create instance
    new_feature = NewFeature(name=data['name'])
    db.session.add(new_feature)
    db.session.commit()
    
    return create_success_response('Feature created', new_feature.to_dict(), 201)
```

#### 3. Register Blueprint
```python
# app.py
from routes.new_feature_routes import new_feature_bp
app.register_blueprint(new_feature_bp, url_prefix='/api/new-feature')
```

### Frontend Feature Development

#### 1. Add API Function
```javascript
/**
 * Create a new feature instance.
 * 
 * @param {string} name - Feature name
 * @returns {Promise<Object>} Created feature data
 */
async function createNewFeature(name) {
    try {
        const response = await apiRequest('/new-feature/create', {
            method: 'POST',
            body: JSON.stringify({ name })
        });
        
        showAlert('Feature created successfully!', 'success');
        return response;
    } catch (error) {
        showAlert(error.message, 'error');
        throw error;
    }
}
```

#### 2. Add UI Function
```javascript
/**
 * Show the create feature modal.
 */
function showCreateFeatureModal() {
    const modal = document.getElementById('createFeatureModal');
    const modalInstance = new bootstrap.Modal(modal);
    modalInstance.show();
}

/**
 * Handle create feature form submission.
 */
async function handleCreateFeature() {
    const nameInput = document.getElementById('featureName');
    const name = nameInput.value.trim();
    
    if (!name) {
        showAlert('Feature name is required', 'error');
        return;
    }
    
    try {
        await createNewFeature(name);
        // Close modal and refresh data
        bootstrap.Modal.getInstance(document.getElementById('createFeatureModal')).hide();
        loadFeatures(); // Refresh the features list
    } catch (error) {
        // Error already handled in createNewFeature
    }
}
```

## 🧪 Testing Guidelines

### Backend Testing

#### 1. Unit Tests
```python
# test_new_feature.py
import unittest
from app import create_app
from database import db
from models.new_feature import NewFeature

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_create_new_feature(self):
        response = self.client.post('/api/new-feature/create', 
                                  json={'name': 'Test Feature'})
        self.assertEqual(response.status_code, 201)
        self.assertIn('Feature created', response.json['message'])
```

#### 2. Integration Tests
```python
def test_user_workflow(self):
    # Register user
    response = self.client.post('/api/user/register', 
                              json={'username': 'test', 'email': 'test@test.com', 'password': 'password'})
    self.assertEqual(response.status_code, 201)
    
    # Login user
    response = self.client.post('/api/user/login', 
                              json={'email': 'test@test.com', 'password': 'password'})
    self.assertEqual(response.status_code, 200)
```

### Frontend Testing

#### 1. Manual Testing Checklist
- [ ] User registration works
- [ ] User login works
- [ ] Dashboard loads correctly
- [ ] Contest creation works
- [ ] Logout works
- [ ] Error messages display properly
- [ ] Responsive design works on mobile

#### 2. Browser Testing
Test in multiple browsers:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🚀 Deployment Process

### Development to Production

#### 1. Code Review Checklist
- [ ] All functions have proper documentation
- [ ] Error handling is comprehensive
- [ ] Security measures are in place
- [ ] Database queries are optimized
- [ ] Frontend validation is complete
- [ ] Tests pass successfully

#### 2. Production Configuration
```python
# config.py - Production settings
class ProductionConfig(Config):
    DEBUG = False
    JWT_COOKIE_SECURE = True  # Require HTTPS
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',')
```

#### 3. Deployment Steps
```bash
# 1. Update environment variables
export FLASK_ENV=production
export DATABASE_URL=your-production-database-url

# 2. Install production dependencies
pip install gunicorn

# 3. Run database migrations
python init_db.py

# 4. Start production server
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 🔍 Debugging Guide

### Common Issues and Solutions

#### 1. Authentication Issues
- **Problem**: "Missing Authorization Header"
- **Solution**: Check JWT cookie configuration and CSRF token handling

#### 2. Database Connection Issues
- **Problem**: "Database connection failed"
- **Solution**: Verify DATABASE_URL and database server status

#### 3. Frontend API Errors
- **Problem**: "CORS error"
- **Solution**: Check CORS configuration in app.py

#### 4. Contest Creation Issues
- **Problem**: Contest not appearing in categories
- **Solution**: Verify date fields are properly set and validated

### Debugging Tools

#### Backend Debugging
```python
# Add logging for debugging
import logging
logging.basicConfig(level=logging.DEBUG)

# Use Flask debug mode
app.run(debug=True)
```

#### Frontend Debugging
```javascript
// Use browser developer tools
console.log('Debug info:', data);

// Check network requests
// Check console for JavaScript errors
// Use breakpoints in functions
```

## 📚 Additional Resources

### Documentation
- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [Bootstrap Documentation](https://getbootstrap.com/docs/)
- [JWT Documentation](https://jwt.io/)

### Best Practices
- Follow RESTful API design principles
- Use meaningful variable and function names
- Add comprehensive error handling
- Write tests for new functionality
- Document all public functions
- Keep functions small and focused
- Use consistent code formatting

---

This development guide provides the foundation for contributing to the WikiContest platform. For specific questions or clarifications, refer to the code comments or create an issue in the repository.
