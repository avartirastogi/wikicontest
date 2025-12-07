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
- MediaWiki API utilities
"""

import re
import requests
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Tuple
from urllib.parse import urlparse, unquote, parse_qs
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


# =============================================================================
# MEDIAWIKI API UTILITIES
# =============================================================================

def extract_page_title_from_url(article_link: str) -> Optional[str]:
    """
    Extract page title from a MediaWiki article URL.

    This function handles various MediaWiki URL formats:
    - Standard format: /wiki/Page_Title
    - Query format: ?title=Page_Title
    - Other formats: /path/to/Page_Title

    Args:
        article_link (str): Full URL to the article

    Returns:
        Optional[str]: Extracted page title, or None if extraction fails

    Example:
        >>> extract_page_title_from_url('https://en.wikipedia.org/wiki/Example')
        'Example'
        >>> extract_page_title_from_url('https://en.wikipedia.org/w/index.php?title=Example')
        'Example'
    """
    try:
        url_obj = urlparse(article_link)
        base_url = f"{url_obj.scheme}://{url_obj.netloc}"

        # Extract page title from URL
        page_title = ''
        if '/wiki/' in url_obj.path:
            page_title = unquote(url_obj.path.split('/wiki/')[1])
        elif 'title=' in url_obj.query:
            query_params = parse_qs(url_obj.query)
            page_title = unquote(query_params.get('title', [''])[0])
        else:
            parts = url_obj.path.split('/')
            page_title = unquote(parts[-1]) if parts else ''

        return page_title if page_title else None
    except Exception:
        return None


def get_oldest_revision_author(revisions: List[Dict[str, Any]]) -> Optional[str]:
    """
    Extract author from the oldest revision (creation revision).

    This function handles cases where the 'user' field might be missing
    and falls back to 'userid' if available.

    Args:
        revisions (List[Dict[str, Any]]): List of revision dictionaries

    Returns:
        Optional[str]: Author name or 'User ID: {userid}' or None

    Example:
        >>> revisions = [{'user': 'John', 'userid': 123}, {'user': 'Jane', 'userid': 456}]
        >>> get_oldest_revision_author(revisions)
        'Jane'  # Returns author from oldest (last) revision
    """
    if not revisions or len(revisions) == 0:
        return None

    # Get oldest revision (creation revision)
    # If we have multiple revisions, the last one is the oldest
    # If we only have one revision, it's both the newest and oldest
    if len(revisions) > 1:
        oldest_revision = revisions[-1]
    else:
        oldest_revision = revisions[0]

    # Extract author from oldest revision (creation revision)
    # Try 'user' field first, then 'userid' as fallback
    article_author = oldest_revision.get('user')
    if not article_author:
        userid = oldest_revision.get('userid')
        if userid:
            article_author = f'User ID: {userid}'
        else:
            article_author = None

    return article_author


def get_latest_revision_author(revisions: List[Dict[str, Any]]) -> Optional[str]:
    """
    Extract author from the latest revision (most recent revision at submission time).

    This function handles cases where the 'user' field might be missing
    and falls back to 'userid' if available.

    When revisions are fetched with rvdir='older', the first revision
    in the array is the newest (latest) revision.

    Args:
        revisions (List[Dict[str, Any]]): List of revision dictionaries
            (with rvdir='older', revisions[0] is the latest)

    Returns:
        Optional[str]: Author name or 'User ID: {userid}' or None

    Example:
        >>> revisions = [{'user': 'John', 'userid': 123}, {'user': 'Jane', 'userid': 456}]
        >>> get_latest_revision_author(revisions)
        'John'  # Returns author from latest (first) revision
    """
    if not revisions or len(revisions) == 0:
        return None

    # Get latest revision (newest revision)
    # With rvdir='older', the first revision is the newest (latest)
    latest_revision = revisions[0]

    # Extract author from latest revision
    # Try 'user' field first, then 'userid' as fallback
    article_author = latest_revision.get('user')
    if not article_author:
        userid = latest_revision.get('userid')
        if userid:
            article_author = f'User ID: {userid}'
        else:
            article_author = None

    return article_author


def build_mediawiki_revisions_api_params(page_title: str) -> Dict[str, Any]:
    """
    Build MediaWiki API parameters for querying article revisions.

    This function creates the standard API parameters used to fetch
    article information including revisions with author and size data.

    Args:
        page_title (str): Page title to query

    Returns:
        Dict[str, Any]: API parameters dictionary

    Example:
        >>> params = build_mediawiki_revisions_api_params('Example')
        >>> params['action']
        'query'
    """
    return {
        'action': 'query',
        'titles': page_title,
        'format': 'json',
        'formatversion': '2',  # Use formatversion=2 for cleaner JSON structure
        'prop': 'info|revisions',
        'rvprop': 'timestamp|user|userid|comment|size',  # Include userid as fallback
        'rvlimit': '2',  # Get 2 revisions: newest and oldest
        'rvdir': 'older',  # Start from newest, get newest first
        'redirects': 'true',  # Follow redirects automatically
        'converttitles': 'true'  # Convert titles to canonical form
    }


def get_mediawiki_headers() -> Dict[str, str]:
    """
    Get standard headers for MediaWiki API requests.

    MediaWiki API requires a User-Agent header to identify the application.
    This function provides the standard headers used across all API requests.

    Returns:
        Dict[str, str]: Headers dictionary with User-Agent

    Example:
        >>> headers = get_mediawiki_headers()
        >>> headers['User-Agent']
        'WikiContest/1.0 (https://wikicontest.toolforge.org; contact@wikicontest.org) Python/requests'
    """
    return {
        'User-Agent': (
            'WikiContest/1.0 (https://wikicontest.toolforge.org; '
            'contact@wikicontest.org) Python/requests'
        )
    }


def get_article_size_at_timestamp(article_link: str, timestamp: datetime) -> Optional[int]:
    """
    Get the byte size of an article at a specific timestamp using MediaWiki API.
    
    This function queries the MediaWiki API to find the revision of an article
    that existed at or before the given timestamp, and returns its size in bytes.
    
    Args:
        article_link (str): Full URL to the article
        timestamp (datetime): Timestamp to get article size for (UTC)
        
    Returns:
        Optional[int]: Article size in bytes at the timestamp, or None if:
            - Article doesn't exist
            - API request fails
            - No revision found at or before the timestamp
            
    Example:
        >>> from datetime import datetime
        >>> size = get_article_size_at_timestamp(
        ...     'https://en.wikipedia.org/wiki/Example',
        ...     datetime(2024, 1, 15, 0, 0, 0)
        ... )
        >>> print(size)
        5000
    """
    try:
        # Extract page title from URL using shared utility function
        page_title = extract_page_title_from_url(article_link)
        if not page_title:
            return None

        # Parse the article URL to extract base URL
        url_obj = urlparse(article_link)
        base_url = f"{url_obj.scheme}://{url_obj.netloc}"
        
        # Convert datetime to MediaWiki API timestamp format (ISO 8601)
        # Format: YYYY-MM-DDTHH:MM:SSZ
        api_timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
        
        # Build MediaWiki API URL
        api_url = f"{base_url}/w/api.php"
        
        # Query for revision at or before the specified timestamp
        # Use rvend to get the latest revision before or at the timestamp
        # Use rvdir='older' to get revisions going backwards from the timestamp
        api_params = {
            'action': 'query',
            'titles': page_title,
            'format': 'json',
            'formatversion': '2',
            'prop': 'revisions',
            'rvprop': 'timestamp|size',
            'rvlimit': '1',  # Only need the latest revision at or before timestamp
            'rvend': api_timestamp,  # Get revision at or before this timestamp
            'rvdir': 'older',  # Go backwards from timestamp
            'redirects': 'true',
            'converttitles': 'true'
        }
        
        # Make request to MediaWiki API using shared headers
        headers = get_mediawiki_headers()
        response = requests.get(api_url, params=api_params, headers=headers, timeout=10)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        
        # Check for API errors
        if 'error' in data:
            return None
        
        # Parse response
        pages = data.get('query', {}).get('pages', [])
        if not pages or len(pages) == 0:
            return None
        
        page_data = pages[0]
        
        # Check if page exists
        is_missing = page_data.get('missing', False)
        page_id = str(page_data.get('pageid', ''))
        
        if is_missing or not page_id or page_id == '-1':
            return None
        
        # Get revision information
        revisions = page_data.get('revisions', [])
        if not revisions or len(revisions) == 0:
            return None
        
        # Get the first (and only) revision - this is the latest revision at or before timestamp
        revision = revisions[0]
        size = revision.get('size', 0)
        
        return size if size else None
        
    except Exception:
        # Return None on any error (network, parsing, etc.)
        return None
