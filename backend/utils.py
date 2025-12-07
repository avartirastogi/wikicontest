"""
Utility Functions for WikiContest Application

This module contains common utility functions that are used across
different parts of the application. These functions help maintain
DRY (Don't Repeat Yourself) principles and provide reusable functionality.

Categories:
- Date and time utilities
- String validation utilities
- Response formatting utilities
- File handling utilities
- Permission and access control utilities
"""

import re
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from flask import jsonify


# =============================================================================
# DATE AND TIME UTILITIES
# =============================================================================

def validate_date_string(date_str: str) -> Optional[date]:
    """
    Validate and parse a date string in YYYY-MM-DD format.
    
    This function is commonly used for parsing date inputs from forms
    and API requests. It handles various edge cases and provides
    consistent error handling.
    
    Args:
        date_str (str): Date string to validate and parse
        
    Returns:
        Optional[date]: Parsed date object if valid, None if invalid
        
    Example:
        >>> validate_date_string('2025-10-29')
        datetime.date(2025, 10, 29)
        >>> validate_date_string('invalid-date')
        None
    """
    if not date_str or not isinstance(date_str, str):
        return None
    
    try:
        # Parse the date string using the standard ISO format
        parsed_date = datetime.strptime(date_str.strip(), '%Y-%m-%d').date()
        return parsed_date
    except ValueError:
        # Return None for invalid date formats
        return None


def format_date_for_display(date_obj: date) -> str:
    """
    Format a date object for user-friendly display.
    
    Args:
        date_obj (date): Date object to format
        
    Returns:
        str: Formatted date string
        
    Example:
        >>> format_date_for_display(date(2025, 10, 29))
        'October 29, 2025'
    """
    if not isinstance(date_obj, date):
        return 'Invalid Date'
    
    return date_obj.strftime('%B %d, %Y')


def get_date_range_days(start_date: date, end_date: date) -> int:
    """
    Calculate the number of days between two dates.
    
    Args:
        start_date (date): Start date
        end_date (date): End date
        
    Returns:
        int: Number of days between the dates
        
    Example:
        >>> get_date_range_days(date(2025, 10, 29), date(2025, 11, 4))
        6
    """
    if not isinstance(start_date, date) or not isinstance(end_date, date):
        return 0
    
    return (end_date - start_date).days


# =============================================================================
# STRING VALIDATION UTILITIES
# =============================================================================

def validate_email(email: str) -> bool:
    """
    Validate email address format using regex pattern.
    
    This function uses a comprehensive regex pattern to validate
    email addresses according to RFC standards.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
        
    Example:
        >>> validate_email('user@example.com')
        True
        >>> validate_email('invalid-email')
        False
    """
    if not email or not isinstance(email, str):
        return False
    
    # Comprehensive email regex pattern
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_username(username: str) -> bool:
    """
    Validate username format and length.
    
    Usernames must be 3-20 characters long and contain only
    alphanumeric characters and underscores.
    
    Args:
        username (str): Username to validate
        
    Returns:
        bool: True if username format is valid, False otherwise
        
    Example:
        >>> validate_username('user123')
        True
        >>> validate_username('user@name')
        False
    """
    if not username or not isinstance(username, str):
        return False
    
    # Username pattern: 3-20 characters, alphanumeric and underscores only
    pattern = r'^[a-zA-Z0-9_]{3,20}$'
    return re.match(pattern, username.strip()) is not None


def validate_password_strength(password: str) -> Dict[str, Any]:
    """
    Validate password strength and return detailed feedback.
    
    Args:
        password (str): Password to validate
        
    Returns:
        Dict[str, Any]: Validation result with score and feedback
        
    Example:
        >>> validate_password_strength('weak')
        {'valid': False, 'score': 1, 'feedback': ['Password too short']}
    """
    if not password or not isinstance(password, str):
        return {
            'valid': False,
            'score': 0,
            'feedback': ['Password is required']
        }
    
    feedback = []
    score = 0
    
    # Length check
    if len(password) < 6:
        feedback.append('Password must be at least 6 characters long')
    else:
        score += 1
    
    # Character variety checks
    if re.search(r'[a-z]', password):
        score += 1
    else:
        feedback.append('Password should contain lowercase letters')
    
    if re.search(r'[A-Z]', password):
        score += 1
    else:
        feedback.append('Password should contain uppercase letters')
    
    if re.search(r'[0-9]', password):
        score += 1
    else:
        feedback.append('Password should contain numbers')
    
    if re.search(r'[^a-zA-Z0-9]', password):
        score += 1
    else:
        feedback.append('Password should contain special characters')
    
    return {
        'valid': score >= 3,
        'score': score,
        'feedback': feedback
    }


# =============================================================================
# RESPONSE FORMATTING UTILITIES
# =============================================================================

def create_success_response(message: str, data: Any = None, status_code: int = 200) -> tuple:
    """
    Create a standardized success response.
    
    Args:
        message (str): Success message
        data (Any): Optional data to include in response
        status_code (int): HTTP status code
        
    Returns:
        tuple: Flask response tuple (jsonify, status_code)
        
    Example:
        >>> create_success_response('User created', {'id': 1})
        ({'message': 'User created', 'data': {'id': 1}}, 201)
    """
    response_data = {'message': message}
    
    if data is not None:
        response_data['data'] = data
    
    return jsonify(response_data), status_code


def create_error_response(message: str, status_code: int = 400, details: Any = None) -> tuple:
    """
    Create a standardized error response.
    
    Args:
        message (str): Error message
        status_code (int): HTTP status code
        details (Any): Optional error details
        
    Returns:
        tuple: Flask response tuple (jsonify, status_code)
        
    Example:
        >>> create_error_response('Validation failed', 400, ['Field required'])
        ({'error': 'Validation failed', 'details': ['Field required']}, 400)
    """
    response_data = {'error': message}
    
    if details is not None:
        response_data['details'] = details
    
    return jsonify(response_data), status_code


def create_paginated_response(items: List[Any], page: int, per_page: int, total: int) -> Dict[str, Any]:
    """
    Create a paginated response structure.
    
    Args:
        items (List[Any]): List of items for current page
        page (int): Current page number
        per_page (int): Number of items per page
        total (int): Total number of items
        
    Returns:
        Dict[str, Any]: Paginated response structure
        
    Example:
        >>> create_paginated_response([1, 2, 3], 1, 10, 25)
        {'items': [1, 2, 3], 'pagination': {'page': 1, 'per_page': 10, 'total': 25, 'pages': 3}}
    """
    total_pages = (total + per_page - 1) // per_page  # Ceiling division
    
    return {
        'items': items,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


# =============================================================================
# DATA PROCESSING UTILITIES
# =============================================================================

def sanitize_string(text: str, max_length: int = None) -> str:
    """
    Sanitize a string by trimming whitespace and optionally limiting length.
    
    Args:
        text (str): String to sanitize
        max_length (int): Optional maximum length
        
    Returns:
        str: Sanitized string
        
    Example:
        >>> sanitize_string('  hello world  ', 10)
        'hello worl'
    """
    if not text or not isinstance(text, str):
        return ''
    
    # Trim whitespace
    sanitized = text.strip()
    
    # Limit length if specified
    if max_length and len(sanitized) > max_length:
        sanitized = sanitized[:max_length]
    
    return sanitized


def parse_comma_separated_list(text: str) -> List[str]:
    """
    Parse a comma-separated string into a list of trimmed strings.
    
    Args:
        text (str): Comma-separated string
        
    Returns:
        List[str]: List of trimmed strings
        
    Example:
        >>> parse_comma_separated_list('admin, user1, user2')
        ['admin', 'user1', 'user2']
    """
    if not text or not isinstance(text, str):
        return []
    
    # Split by comma and trim each item
    items = [item.strip() for item in text.split(',')]
    
    # Remove empty items
    return [item for item in items if item]


def safe_int_conversion(value: Any, default: int = 0) -> int:
    """
    Safely convert a value to an integer with a default fallback.
    
    Args:
        value (Any): Value to convert
        default (int): Default value if conversion fails
        
    Returns:
        int: Converted integer or default value
        
    Example:
        >>> safe_int_conversion('123', 0)
        123
        >>> safe_int_conversion('invalid', 0)
        0
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


# =============================================================================
# PERMISSION AND ACCESS CONTROL UTILITIES
# =============================================================================

def can_view_submissions(user, contest) -> bool:
    """
    Check if user has permission to view submissions for a contest.
    
    Users can view submissions if they are:
    - An admin
    - The contest creator
    - A jury member of the contest
    
    Args:
        user: User object with permission methods
        contest: Contest object to check permissions for
        
    Returns:
        bool: True if user has permission, False otherwise
        
    Example:
        >>> can_view_submissions(admin_user, contest)
        True
        >>> can_view_submissions(regular_user, contest)
        False
    """
    return (user.is_admin() or
            user.is_contest_creator(contest) or
            user.is_jury_member(contest))


def validate_contest_submission_access(contest_id: int, user, contest_model) -> Tuple[Any, Optional[tuple]]:
    """
    Validate that a contest exists and user has permission to view submissions.
    
    This function extracts the common validation logic used in multiple routes
    to check contest existence and submission viewing permissions. It helps
    eliminate code duplication across different route handlers.
    
    Args:
        contest_id: ID of the contest to validate
        user: User object (from request.current_user)
        contest_model: Contest model class to query from database
        
    Returns:
        Tuple[Any, Optional[tuple]]: 
            - First element: Contest object if valid, None if invalid
            - Second element: Error response tuple (jsonify, status_code) if invalid, None if valid
            
    Example:
        >>> contest, error = validate_contest_submission_access(1, user, Contest)
        >>> if error:
        ...     return error  # Return 404 or 403 error
        >>> # Use contest object
    """
    # Get contest from database
    contest = contest_model.query.get(contest_id)
    
    # Check if contest exists
    if not contest:
        return None, (jsonify({'error': 'Contest not found'}), 404)
    
    # Check if user has permission to view submissions
    if not can_view_submissions(user, contest):
        return None, (jsonify({
            'error': 'You are not allowed to view submissions for this contest'
        }), 403)
    
    # Contest exists and user has permission
    return contest, None
