"""
User Routes for WikiContest Application
Handles user registration, login, logout, and dashboard functionality
"""

from flask import Blueprint, request, jsonify, make_response, session, redirect, url_for, current_app
from flask_jwt_extended import create_access_token, set_access_cookies, unset_jwt_cookies
from models.user import User
from middleware.auth import require_auth, require_role, handle_errors, validate_json_data
import re
from database import db
import mwoauth

# Create blueprint
user_bp = Blueprint('user', __name__)

def validate_email(email):
    """
    Validate email format
    
    Args:
        email: Email string to validate
        
    Returns:
        bool: True if valid email, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_username(username):
    """
    Validate username format
    
    Args:
        username: Username string to validate
        
    Returns:
        bool: True if valid username, False otherwise
    """
    # Username should be 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username) is not None

@user_bp.route('/register', methods=['POST'])
@handle_errors
@validate_json_data(['username', 'email', 'password'])
def register():
    """
    Register a new user
    
    Expected JSON data:
        username: Unique username (3-20 chars, alphanumeric + underscore)
        email: Valid email address
        password: Password (min 6 chars)
        role: Optional role (defaults to 'user')
    
    Returns:
        JSON response with success message and user ID
    """
    data = request.validated_data
    username = data['username'].strip()
    email = data['email'].strip().lower()
    password = data['password']
    role = data.get('role', 'user')
    
    # Validate input data
    if not validate_username(username):
        return jsonify({'error': 'Username must be 3-20 characters, alphanumeric and underscores only'}), 400
    
    if not validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters long'}), 400
    
    if role not in ['user', 'admin']:
        return jsonify({'error': 'Invalid role'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=username).first():
        return jsonify({'error': 'Username already exists'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400
    
    # Create new user
    try:
        user = User(username=username, email=email, password=password, role=role)
        user.save()
        
        return jsonify({
            'message': 'User created successfully',
            'userId': user.id,
            'username': user.username
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create user'}), 500

@user_bp.route('/login', methods=['POST'])
@handle_errors
def login():
    """
    Login user and create JWT token
    
    Expected JSON data:
        email: User's email address
        password: User's password
    
    Returns:
        JSON response with success message and JWT token in cookie
    """
    # Get JSON data directly
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No JSON data provided'}), 400
    
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    
    if not email or not password:
        return jsonify({'error': 'Email and password required'}), 400
    
    # Find user by email
    user = User.query.filter_by(email=email).first()
    
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401
    
    try:
        # Create JWT token
        access_token = create_access_token(identity=str(user.id))
        
        # Create response
        response = make_response(jsonify({
            'message': 'Login successful',
            'userId': user.id,
            'username': user.username
        }))
        
        # Set JWT token in HTTP-only cookie
        set_access_cookies(response, access_token)
        
        return response, 200
        
    except Exception as e:
        print(f"Error in login process: {str(e)}")
        return jsonify({'error': 'Login failed'}), 500

@user_bp.route('/logout', methods=['POST'])
@require_auth
@handle_errors
def logout():
    """
    Logout user and clear JWT token
    
    Returns:
        JSON response with success message
    """
    response = make_response(jsonify({'message': 'Logout successful'}))
    unset_jwt_cookies(response)
    return response, 200

@user_bp.route('/dashboard', methods=['GET'])
@require_auth
@handle_errors
def get_dashboard():
    """
    Get user dashboard data
    
    Returns:
        JSON response with user's dashboard information
    """
    user = request.current_user
    
    # Get user's total score
    total_score = user.score
    
    # Get contest-wise scores
    from models.submission import Submission
    from models.contest import Contest
    
    contest_scores = db.session.query(
        Contest.id.label('contest_id'),
        Contest.name.label('contest_name'),
        db.func.sum(Submission.score).label('contest_score'),
        db.func.count(Submission.id).label('submission_count')
    ).join(Submission).filter(
        Submission.user_id == user.id
    ).group_by(Contest.id, Contest.name).order_by(Contest.name).all()
    
    # Get all user's submissions grouped by contest
    submissions_query = db.session.query(
        Submission,
        Contest.name.label('contest_name')
    ).join(Contest).filter(
        Submission.user_id == user.id
    ).order_by(Submission.submitted_at.desc()).all()
    
    # Group submissions by contest
    submissions_by_contest = {}
    for submission, contest_name in submissions_query:
        contest_id = submission.contest_id
        if contest_id not in submissions_by_contest:
            submissions_by_contest[contest_id] = {
                'contest_id': contest_id,
                'contest_name': contest_name,
                'submissions': []
            }
        submissions_by_contest[contest_id]['submissions'].append(submission.to_dict())
    
    # Get contests created by user
    created_contests = Contest.query.filter_by(created_by=user.username).all()
    created_contests_data = []
    for contest in created_contests:
        contest_data = contest.to_dict()
        contest_data['submission_count'] = contest.get_submission_count()
        created_contests_data.append(contest_data)
    
    # Get contests where user is a jury member
    jury_contests = Contest.query.filter(
        Contest.jury_members.like(f'%{user.username}%')
    ).all()
    jury_contests_data = []
    for contest in jury_contests:
        contest_data = contest.to_dict()
        contest_data['submission_count'] = contest.get_submission_count()
        jury_contests_data.append(contest_data)
    
    return jsonify({
        'username': user.username,
        'total_score': total_score,
        'contest_wise_scores': [
            {
                'contest_id': row.contest_id,
                'contest_name': row.contest_name,
                'contest_score': row.contest_score or 0,
                'submission_count': row.submission_count
            }
            for row in contest_scores
        ],
        'submissions_by_contest': list(submissions_by_contest.values()),
        'created_contests': created_contests_data,
        'jury_contests': jury_contests_data
    }), 200

@user_bp.route('/all', methods=['GET'])
@require_role('admin')
@handle_errors
def get_all_users():
    """
    Get all users (admin only)
    
    Returns:
        JSON response with list of all users
    """
    users = User.query.all()
    return jsonify([user.to_dict() for user in users]), 200

@user_bp.route('/profile', methods=['GET'])
@require_auth
@handle_errors
def get_profile():
    """
    Get current user's profile
    
    Returns:
        JSON response with user profile data
    """
    user = request.current_user
    return jsonify(user.to_dict()), 200

@user_bp.route('/profile', methods=['PUT'])
@require_auth
@handle_errors
@validate_json_data(['username', 'email'])
def update_profile():
    """
    Update current user's profile
    
    Expected JSON data:
        username: New username
        email: New email address
    
    Returns:
        JSON response with success message
    """
    user = request.current_user
    data = request.validated_data
    
    new_username = data['username'].strip()
    new_email = data['email'].strip().lower()
    
    # Validate input data
    if not validate_username(new_username):
        return jsonify({'error': 'Username must be 3-20 characters, alphanumeric and underscores only'}), 400
    
    if not validate_email(new_email):
        return jsonify({'error': 'Invalid email format'}), 400
    
    # Check if username is already taken by another user
    existing_user = User.query.filter(
        User.username == new_username,
        User.id != user.id
    ).first()
    if existing_user:
        return jsonify({'error': 'Username already exists'}), 400
    
    # Check if email is already taken by another user
    existing_email = User.query.filter(
        User.email == new_email,
        User.id != user.id
    ).first()
    if existing_email:
        return jsonify({'error': 'Email already exists'}), 400
    
    # Update user data
    user.username = new_username
    user.email = new_email
    user.save()
    
    return jsonify({'message': 'Profile updated successfully'}), 200

# =============================================================================
# OAUTH ROUTES (Wikimedia OAuth 1.0a)
# =============================================================================

@user_bp.route('/oauth/login', methods=['GET'])
@handle_errors
def oauth_login():
    """
    Initiate OAuth login with Wikimedia.
    
    This route starts the OAuth 1.0a authentication flow with Wikimedia.
    It uses the OAuth consumer credentials from the .env file.
    
    Returns:
        Redirect to Wikimedia OAuth authorization page
    """
    # Get OAuth configuration from app config (loaded from .env)
    consumer_key = current_app.config.get('CONSUMER_KEY')
    consumer_secret = current_app.config.get('CONSUMER_SECRET')
    mw_uri = current_app.config.get('OAUTH_MWURI', 'https://meta.wikimedia.org/w/index.php')
    
    # Check if OAuth is configured
    if not consumer_key or not consumer_secret:
        return jsonify({
            'error': 'OAuth not configured. Please set CONSUMER_KEY and CONSUMER_SECRET in .env file'
        }), 500
    
    try:
        # Generate OAuth request token
        # The callback URL should match what's registered in OAuth consumer
        callback_url = request.url_root.rstrip('/') + '/api/user/oauth/callback'
        
        # Create OAuth consumer
        consumer_token = mwoauth.ConsumerToken(consumer_key, consumer_secret)
        
        # Get request token from Wikimedia
        redirect_url, request_token = mwoauth.initiate(
            mw_uri,
            consumer_token,
            callback=callback_url
        )
        
        # Store request token in session for later verification
        session['request_token'] = request_token.key
        session['request_secret'] = request_token.secret
        
        # Redirect user to Wikimedia for authorization
        return redirect(redirect_url)
        
    except Exception as e:
        current_app.logger.error(f'OAuth initiation error: {str(e)}')
        return jsonify({
            'error': 'Failed to initiate OAuth login',
            'details': str(e)
        }), 500

@user_bp.route('/oauth/callback', methods=['GET'])
@handle_errors
def oauth_callback():
    """
    Handle OAuth callback from Wikimedia.
    
    This route is called by Wikimedia after the user authorizes the application.
    It exchanges the request token for an access token and creates/updates the user.
    
    Query parameters:
        oauth_verifier: Verification code from Wikimedia
        oauth_token: Request token (should match session)
    
    Returns:
        Redirect to frontend with success message or error
    """
    # Get OAuth configuration from app config
    consumer_key = current_app.config.get('CONSUMER_KEY')
    consumer_secret = current_app.config.get('CONSUMER_SECRET')
    mw_uri = current_app.config.get('OAUTH_MWURI', 'https://meta.wikimedia.org/w/index.php')
    
    # Get OAuth parameters from callback
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_token = request.args.get('oauth_token')
    
    # Get stored request token from session
    request_token_key = session.get('request_token')
    request_secret = session.get('request_secret')
    
    # Validate callback parameters
    if not oauth_verifier or not oauth_token:
        return jsonify({'error': 'Missing OAuth parameters'}), 400
    
    if not request_token_key or not request_secret:
        return jsonify({'error': 'OAuth session expired. Please try again.'}), 400
    
    if oauth_token != request_token_key:
        return jsonify({'error': 'Invalid OAuth token'}), 400
    
    try:
        # Create consumer and request tokens
        consumer_token = mwoauth.ConsumerToken(consumer_key, consumer_secret)
        request_token = mwoauth.RequestToken(request_token_key, request_secret)
        
        # Exchange request token for access token
        access_token = mwoauth.complete(
            mw_uri,
            consumer_token,
            request_token,
            oauth_verifier
        )
        
        # Get user identity from Wikimedia
        identity = mwoauth.identify(mw_uri, consumer_token, access_token)
        
        # Extract user information
        username = identity.get('username', '')
        user_id = identity.get('sub', '')
        
        if not username:
            return jsonify({'error': 'Failed to get user information from Wikimedia'}), 500
        
        # Find or create user in database
        # Use username as the unique identifier
        user = User.query.filter_by(username=username).first()
        
        if not user:
            # Create new user from OAuth
            # OAuth users don't need a password, but User model requires one
            # Generate a random secure password that will never be used
            import secrets
            random_password = secrets.token_urlsafe(32)
            # User.__init__ will automatically hash the password via set_password
            user = User(
                username=username,
                email=f'{username}@wikimedia.oauth',  # Placeholder email
                password=random_password,  # Random password (OAuth users won't use it)
                role='user'
            )
            user.save()
        else:
            # Update existing user if needed
            # OAuth users might not have a password set
            pass
        
        # Create JWT token for the user
        access_token_jwt = create_access_token(identity=str(user.id))
        
        # Clear OAuth session data
        session.pop('request_token', None)
        session.pop('request_secret', None)
        
        # Create response with redirect to frontend
        response = make_response(redirect('/'))
        
        # Set JWT token in HTTP-only cookie
        set_access_cookies(response, access_token_jwt)
        
        return response
        
    except Exception as e:
        current_app.logger.error(f'OAuth callback error: {str(e)}')
        return jsonify({
            'error': 'OAuth authentication failed',
            'details': str(e)
        }), 500