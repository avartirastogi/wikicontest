"""
Contest Routes for WikiContest Application
Handles contest creation, retrieval, and management functionality
"""

from flask import Blueprint, request, jsonify
from models.contest import Contest
from models.user import User
from models.submission import Submission
from middleware.auth import require_auth, require_contest_permission, handle_errors, validate_json_data
from datetime import datetime, date
from database import db

# Create blueprint
contest_bp = Blueprint('contest', __name__)

def validate_date_string(date_str):
    """
    Validate date string format (YYYY-MM-DD)
    
    Args:
        date_str: Date string to validate
        
    Returns:
        date: Parsed date object or None if invalid
    """
    if not date_str:
        return None
    
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None

@contest_bp.route('/', methods=['GET'])
@require_auth
@handle_errors
def get_all_contests():
    """
    Get all contests categorized by status
    Requires authentication - users must be logged in to view contests.
    
    Returns:
        JSON response with contests categorized as current, upcoming, and past
    """
    contests = Contest.query.order_by(Contest.created_at.desc()).all()
    
    current = []
    upcoming = []
    past = []
    
    for contest in contests:
        contest_data = contest.to_dict()
        
        if contest.is_active():
            current.append(contest_data)
        elif contest.is_upcoming():
            upcoming.append(contest_data)
        elif contest.is_past():
            past.append(contest_data)
    
    return jsonify({
        'current': current,
        'upcoming': upcoming,
        'past': past
    }), 200

@contest_bp.route('/', methods=['POST'])
@require_auth
@handle_errors
@validate_json_data(['name', 'project_name', 'jury_members'])
def create_contest():
    """
    Create a new contest
    
    Expected JSON data:
        name: Name of the contest
        project_name: Name of the associated project
        jury_members: List of jury member usernames
        code_link: Optional link to contest's code repository
        description: Optional description of the contest
        start_date: Optional start date (YYYY-MM-DD)
        end_date: Optional end date (YYYY-MM-DD)
        rules: Optional rules object
        marks_setting_accepted: Optional points for accepted submissions
        marks_setting_rejected: Optional points for rejected submissions
    
    Returns:
        JSON response with success message and contest ID
    """
    user = request.current_user
    data = request.validated_data
    
    # Validate required fields
    name = data['name'].strip()
    project_name = data['project_name'].strip()
    jury_members = data['jury_members']
    
    if not name:
        return jsonify({'error': 'Contest name is required'}), 400
    
    if not project_name:
        return jsonify({'error': 'Project name is required'}), 400
    
    if not isinstance(jury_members, list) or len(jury_members) == 0:
        return jsonify({'error': 'Jury members must be a non-empty array of usernames'}), 400
    
    # Validate jury members exist
    existing_users = User.query.filter(User.username.in_(jury_members)).all()
    existing_usernames = [user.username for user in existing_users]
    missing_users = [username for username in jury_members if username not in existing_usernames]
    
    if missing_users:
        return jsonify({'error': f'These jury members do not exist: {", ".join(missing_users)}'}), 400
    
    # Parse optional fields
    # Handle code_link: can be None (from frontend), empty string, or a URL
    code_link_value = data.get('code_link')
    if code_link_value is None or code_link_value == '':
        code_link = None
    else:
        code_link = str(code_link_value).strip() or None
    
    # Handle description: can be None, empty string, or text
    description_value = data.get('description')
    if description_value is None or description_value == '':
        description = None
    else:
        description = str(description_value).strip() or None
    
    # Parse dates
    start_date = validate_date_string(data.get('start_date'))
    end_date = validate_date_string(data.get('end_date'))
    
    # Validate date logic
    if start_date and end_date and start_date >= end_date:
        return jsonify({'error': 'End date must be after start date'}), 400
    
    # Parse rules
    rules = data.get('rules', {})
    if not isinstance(rules, dict):
        rules = {}
    
    # Parse scoring settings
    marks_accepted = data.get('marks_setting_accepted', 0)
    marks_rejected = data.get('marks_setting_rejected', 0)
    
    try:
        marks_accepted = int(marks_accepted)
        marks_rejected = int(marks_rejected)
    except (ValueError, TypeError):
        return jsonify({'error': 'Marks settings must be valid integers'}), 400
    
    # Create contest
    try:
        contest = Contest(
            name=name,
            project_name=project_name,
            created_by=user.username,
            code_link=code_link,
            description=description,
            start_date=start_date,
            end_date=end_date,
            rules=rules,
            marks_setting_accepted=marks_accepted,
            marks_setting_rejected=marks_rejected,
            jury_members=jury_members
        )
        
        contest.save()
        
        return jsonify({
            'message': 'Contest created successfully',
            'contestId': contest.id
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create contest'}), 500

@contest_bp.route('/<int:id>', methods=['GET'])
@require_auth
@handle_errors
def get_contest_by_id(id):
    """
    Get a specific contest by ID
    Requires authentication - users must be logged in to view contest details.
    
    Args:
        id: Contest ID
    
    Returns:
        JSON response with contest data
    """
    contest = Contest.query.get(id)
    
    if not contest:
        return jsonify({'error': 'Contest not found'}), 404
    
    return jsonify(contest.to_dict()), 200

@contest_bp.route('/<int:id>/leaderboard', methods=['GET'])
@require_auth
@handle_errors
def get_contest_leaderboard(id):
    """
    Get leaderboard for a specific contest
    Requires authentication - users must be logged in to view leaderboard.
    
    Args:
        id: Contest ID
    
    Returns:
        JSON response with leaderboard data
    """
    contest = Contest.query.get(id)
    
    if not contest:
        return jsonify({'error': 'Contest not found'}), 404
    
    leaderboard = contest.get_leaderboard()
    
    return jsonify(leaderboard), 200

@contest_bp.route('/<int:id>', methods=['DELETE'])
@require_auth
@handle_errors
def delete_contest(id):
    """
    Delete a contest (admin or creator only)
    
    Args:
        id: Contest ID
    
    Returns:
        JSON response with success message
    """
    user = request.current_user
    contest = Contest.query.get(id)
    
    if not contest:
        return jsonify({'error': 'Contest not found'}), 404
    
    # Check permissions
    if not (user.is_admin() or user.is_contest_creator(contest)):
        return jsonify({'error': 'You are not allowed to delete this contest'}), 403
    
    try:
        # Delete associated submissions first
        Submission.query.filter_by(contest_id=id).delete()
        
        # Delete contest
        contest.delete()
        
        return jsonify({'message': 'Contest deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to delete contest'}), 500

@contest_bp.route('/<int:id>/submit', methods=['POST'])
@require_auth
@handle_errors
@validate_json_data(['article_title', 'article_link'])
def submit_to_contest(id):
    """
    Submit an entry to a contest
    
    Args:
        id: Contest ID
    
    Expected JSON data:
        article_title: Title of the submitted article
        article_link: URL to the submitted article
    
    Returns:
        JSON response with success message and submission ID
    """
    user = request.current_user
    data = request.validated_data
    
    # Get contest
    contest = Contest.query.get(id)
    if not contest:
        return jsonify({'error': 'Contest not found'}), 404
    
    # Validate submission data
    article_title = data['article_title'].strip()
    article_link = data['article_link'].strip()
    
    if not article_title:
        return jsonify({'error': 'Article title is required'}), 400
    
    if not article_link:
        return jsonify({'error': 'Article link is required'}), 400
    
    # Basic URL validation
    if not (article_link.startswith('http://') or article_link.startswith('https://')):
        return jsonify({'error': 'Article link must be a valid URL'}), 400
    
    # Check if contest is active
    if not contest.is_active():
        if contest.is_upcoming():
            return jsonify({'error': 'Contest has not started yet'}), 400
        elif contest.is_past():
            return jsonify({'error': 'Contest has ended'}), 400
        else:
            return jsonify({'error': 'Contest is not active'}), 400
    
    # Check if user already submitted to this contest
    existing_submission = Submission.query.filter_by(
        user_id=user.id,
        contest_id=id
    ).first()
    
    if existing_submission:
        return jsonify({'error': 'You have already submitted to this contest'}), 400
    
    # Create submission
    try:
        submission = Submission(
            user_id=user.id,
            contest_id=id,
            article_title=article_title,
            article_link=article_link,
            status='pending'
        )
        
        submission.save()
        
        return jsonify({
            'message': 'Submission created successfully',
            'submissionId': submission.id,
            'contest_id': id,
            'article_title': article_title
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'Failed to create submission'}), 500

@contest_bp.route('/<int:id>/submissions', methods=['GET'])
@require_auth
@handle_errors
def get_contest_submissions(id):
    """
    Get all submissions for a specific contest (admin, jury, or creator only)
    
    Args:
        id: Contest ID
    
    Returns:
        JSON response with submissions data
    """
    user = request.current_user
    contest = Contest.query.get(id)
    
    if not contest:
        return jsonify({'error': 'Contest not found'}), 404
    
    # Check permissions
    if not (user.is_admin() or 
            user.is_contest_creator(contest) or 
            user.is_jury_member(contest)):
        return jsonify({'error': 'You are not allowed to view submissions for this contest'}), 403
    
    # Get submissions with user information
    submissions = db.session.query(
        Submission,
        User.username,
        User.email
    ).join(User).filter(
        Submission.contest_id == id
    ).order_by(Submission.submitted_at.desc()).all()
    
    submissions_data = []
    for submission, username, email in submissions:
        submission_data = submission.to_dict(include_user_info=True)
        submission_data.update({
            'username': username,
            'email': email,
            'contest_name': contest.name
        })
        submissions_data.append(submission_data)
    
    return jsonify(submissions_data), 200