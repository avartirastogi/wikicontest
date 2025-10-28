"""
WikiContest Flask Application
Main application entry point for the Python Flask backend

This module initializes the Flask application with all necessary configurations,
extensions, and route blueprints. It serves as the central hub for the WikiContest
platform, handling both API endpoints and static file serving.

Architecture:
- Modular design with separate blueprints for different features
- JWT-based authentication with cookie storage
- CORS enabled for frontend communication
- Database integration with SQLAlchemy ORM
- Comprehensive error handling and logging

Author: WikiContest Development Team
Version: 1.0.0
"""

# Standard library imports
import os
from datetime import timedelta

# Third-party imports
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv

# Local imports
from database import db

# =============================================================================
# CONFIGURATION SETUP
# =============================================================================

# Load environment variables from .env file
# This allows for easy configuration management across different environments
load_dotenv()

def create_app():
    """
    Application factory pattern for creating Flask app instances.
    
    This function creates and configures the Flask application with all
    necessary extensions and settings. Using the factory pattern makes
    the application more testable and allows for different configurations
    in different environments.
    
    Returns:
        Flask: Configured Flask application instance
    """
    # Initialize Flask application
    app = Flask(__name__)
    
    # =========================================================================
    # SECURITY CONFIGURATION
    # =========================================================================
    
    # Secret keys for session management and JWT signing
    # These should be different in production and stored securely
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'rohank10')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'rohank10')
    
    # JWT token expiration time (24 hours)
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    
    # JWT Cookie Configuration for secure token storage
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']  # Store tokens in HTTP-only cookies
    app.config['JWT_COOKIE_SECURE'] = False  # Set to True in production with HTTPS
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True  # Enable CSRF protection
    app.config['JWT_CSRF_IN_COOKIES'] = True  # Include CSRF token in cookies
    
    # =========================================================================
    # DATABASE CONFIGURATION
    # =========================================================================
    
    # Database connection string
    # Supports MySQL, PostgreSQL, SQLite, and other SQLAlchemy-compatible databases
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL', 
        'mysql+pymysql://root:password@localhost/wikicontest'
    )
    
    # Disable SQLAlchemy event system for better performance
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # =========================================================================
    # EXTENSION INITIALIZATION
    # =========================================================================
    
    # Initialize database with the app
    db.init_app(app)
    
    # Initialize JWT manager for token handling
    jwt = JWTManager(app)
    
    # Configure CORS for frontend communication
    # Allows requests from frontend development servers
    CORS(app, origins=[
        'http://localhost:3000',  # React development server
        'http://localhost:5173',  # Vite development server
        'http://localhost:5000'   # Flask development server
    ], supports_credentials=True)
    
    return app

# Create the application instance
app = create_app()

# =============================================================================
# MODEL REGISTRATION
# =============================================================================

# Import models to ensure they are registered with SQLAlchemy
# This is required for database migrations and table creation
from models.user import User
from models.contest import Contest
from models.submission import Submission

# =============================================================================
# ROUTE BLUEPRINT REGISTRATION
# =============================================================================

# Import route blueprints for modular organization
# Each blueprint handles a specific domain of functionality
from routes.user_routes import user_bp
from routes.contest_routes import contest_bp
from routes.submission_routes import submission_bp

# Register blueprints with URL prefixes for API organization
# This creates a clean RESTful API structure
app.register_blueprint(user_bp, url_prefix='/api/user')      # User management endpoints
app.register_blueprint(contest_bp, url_prefix='/api/contest')  # Contest management endpoints
app.register_blueprint(submission_bp, url_prefix='/api/submission')  # Submission management endpoints

# =============================================================================
# AUTHENTICATION ENDPOINTS
# =============================================================================

@app.route('/api/cookie', methods=['GET'])
def check_cookie():
    """
    Check if user is authenticated via JWT cookie.
    
    This endpoint is used by the frontend to verify if a user is currently
    logged in. It reads the JWT token from the HTTP-only cookie and returns
    the user's basic information if the token is valid.
    
    Returns:
        JSON: User information if authenticated, error if not
    """
    from flask_jwt_extended import verify_jwt_in_request, get_jwt_identity
    
    try:
        # Verify the JWT token from the cookie
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        
        # Get user details from database
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'User not found'}), 401
            
        return jsonify({
            'userId': user.id,
            'username': user.username,
            'email': user.email
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'You are not logged in'}), 401

# =============================================================================
# FRONTEND SERVING ROUTES
# =============================================================================

@app.route('/')
def index():
    """
    Serve the main frontend page.
    
    This route serves the main HTML file for the WikiContest frontend.
    All frontend assets are served from the '../frontend' directory.
    """
    return send_from_directory('../frontend', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """
    Serve static files from frontend directory.
    
    This catch-all route serves static assets (CSS, JS, images) for the frontend.
    It allows the Flask app to serve the entire frontend application.
    """
    return send_from_directory('../frontend', filename)

# =============================================================================
# SYSTEM ENDPOINTS
# =============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    
    This endpoint can be used by monitoring systems to check if the
    application is running and responding to requests.
    
    Returns:
        JSON: Application status information
    """
    return jsonify({
        'status': 'healthy', 
        'message': 'WikiContest API is running',
        'version': '1.0.0'
    }), 200

# =============================================================================
# ERROR HANDLERS
# =============================================================================

@app.errorhandler(404)
def not_found(error):
    """
    Handle 404 Not Found errors.
    
    This handler catches all requests to non-existent endpoints and
    returns a consistent JSON error response.
    """
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """
    Handle 500 Internal Server errors.
    
    This handler catches all unhandled exceptions and returns a generic
    error response. It also rolls back any pending database transactions.
    """
    db.session.rollback()
    return jsonify({'error': 'Internal server error'}), 500

# =============================================================================
# APPLICATION STARTUP
# =============================================================================

if __name__ == '__main__':
    """
    Main application entry point.
    
    This section runs when the script is executed directly (not imported).
    It initializes the database tables and starts the Flask development server.
    """
    
    # Initialize database tables
    # This creates all tables defined in the models if they don't exist
    with app.app_context():
        db.create_all()
        print("✓ Database tables initialized successfully")
    
    # Start the Flask development server
    # Debug mode is enabled for development (disable in production)
    print("🚀 Starting WikiContest API server...")
    print("📡 Server will be available at: http://localhost:5000")
    print("🔧 Debug mode: ENABLED")
    
    app.run(
        debug=True,        # Enable debug mode for development
        host='0.0.0.0',    # Allow connections from any IP
        port=5000          # Default Flask development port
    )