"""
Outreach Dashboard API Service

This module provides functions to interact with Wikimedia's Outreach Dashboard API.
It handles URL parsing, validation, and fetching data from various endpoints.
Designed to be extensible for future API endpoints.
"""

import re
from typing import Dict, Optional, Any, List
from urllib.parse import urlparse, urljoin

import requests
from flask import current_app


# Base URL for Outreach Dashboard API
OUTREACH_DASHBOARD_BASE = "https://outreachdashboard.wmflabs.org"
API_TIMEOUT = 10  # seconds


def parse_outreach_url(url: str) -> Dict[str, Optional[str]]:
    """
    Parse an Outreach Dashboard URL to extract school and course_slug.
    
    Accepts URLs in the format:
    - https://outreachdashboard.wmflabs.org/courses/{school}/{course_slug}
    - https://outreachdashboard.wmflabs.org/courses/{school}/{course_slug}/
    - https://outreachdashboard.wmflabs.org/courses/{school}/{course_slug}/course.json
    - https://outreachdashboard.wmflabs.org/courses/{school}/{course_slug}/home
    - https://outreachdashboard.wmflabs.org/courses/{school}/{course_slug}/enroll
    - And other paths (automatically stripped)
    
    Args:
        url: The Outreach Dashboard URL to parse
        
    Returns:
        Dictionary with keys:
            - 'school': School/institution name (or None if not found)
            - 'course_slug': Course slug (or None if not found)
            - 'valid': Boolean indicating if URL format is valid
    """
    if not url or not isinstance(url, str):
        return {'school': None, 'course_slug': None, 'valid': False}
    
    url = url.strip()
    
    # Parse the URL
    try:
        parsed = urlparse(url)
    except Exception:
        return {'school': None, 'course_slug': None, 'valid': False}
    
    # Check if it's an Outreach Dashboard URL
    if 'outreachdashboard.wmflabs.org' not in parsed.netloc:
        return {'school': None, 'course_slug': None, 'valid': False}
    
    # Extract path components
    path = parsed.path.strip('/')
    
    # Split path into components and take only the first 3 parts
    # This handles URLs with suffixes like /home, /enroll, /course.json, etc.
    # Example: courses/school/course/home -> ['courses', 'school', 'course', 'home']
    # We only need: ['courses', 'school', 'course']
    path_parts = path.split('/')
    
    # We need at least 3 parts: courses, school, course_slug
    if len(path_parts) < 3:
        return {'school': None, 'course_slug': None, 'valid': False}
    
    # Check if it starts with 'courses'
    if path_parts[0] != 'courses':
        return {'school': None, 'course_slug': None, 'valid': False}
    
    # Extract school and course_slug (ignore any additional path segments)
    school = path_parts[1]
    course_slug = path_parts[2]
    
    # Validate that school and course_slug are not empty
    if not school or not course_slug:
        return {'school': None, 'course_slug': None, 'valid': False}
    
    return {
        'school': school,
        'course_slug': course_slug,
        'valid': True
    }


def validate_outreach_url(url: str) -> Dict[str, Any]:
    """
    Validate an Outreach Dashboard URL format.
    
    Args:
        url: The URL to validate
        
    Returns:
        Dictionary with keys:
            - 'valid': Boolean indicating if URL is valid
            - 'error': Error message if invalid (None if valid)
    """
    if not url or not isinstance(url, str):
        return {'valid': False, 'error': 'URL is required'}
    
    url = url.strip()
    
    if not url:
        return {'valid': False, 'error': 'URL cannot be empty'}
    
    # Check basic URL format
    if not (url.startswith('http://') or url.startswith('https://')):
        return {'valid': False, 'error': 'URL must start with http:// or https://'}
    
    # Parse the URL
    parsed = parse_outreach_url(url)
    
    if not parsed['valid']:
        return {
            'valid': False,
            'error': 'Invalid Outreach Dashboard URL format. Expected: https://outreachdashboard.wmflabs.org/courses/{school}/{course_slug}'
        }
    
    return {'valid': True, 'error': None}


def _build_api_url(school: str, course_slug: str, endpoint: str) -> str:
    """
    Build API URL for any Outreach Dashboard endpoint.
    
    Args:
        school: School/institution name
        course_slug: Course slug identifier
        endpoint: API endpoint name (e.g., 'course.json', 'users.json')
        
    Returns:
        Full API URL string
    """
    return f"{OUTREACH_DASHBOARD_BASE}/courses/{school}/{course_slug}/{endpoint}"


def _make_api_request(api_url: str) -> Dict[str, Any]:
    """
    Make HTTP request to Outreach Dashboard API with standardized error handling.
    
    Args:
        api_url: Full API URL to request
        
    Returns:
        Dictionary with keys:
            - 'success': Boolean indicating if request was successful
            - 'data': Parsed JSON data if successful (None otherwise)
            - 'error': Error message if failed (None if successful)
    """
    try:
        # Make request to Outreach Dashboard API
        response = requests.get(api_url, timeout=API_TIMEOUT)
        
        if response.status_code == 404:
            return {
                'success': False,
                'data': None,
                'error': 'Resource not found. Please verify the URL is correct.'
            }
        
        if response.status_code != 200:
            return {
                'success': False,
                'data': None,
                'error': f'API returned status code {response.status_code}'
            }
        
        # Parse JSON response
        try:
            data = response.json()
        except ValueError as e:
            return {
                'success': False,
                'data': None,
                'error': f'Failed to parse API response: {str(e)}'
            }
        
        return {
            'success': True,
            'data': data,
            'error': None
        }
            
    except requests.exceptions.Timeout:
        return {
            'success': False,
            'data': None,
            'error': 'Request timed out. The Outreach Dashboard API may be slow or unavailable.'
        }
    except requests.exceptions.ConnectionError:
        return {
            'success': False,
            'data': None,
            'error': 'Failed to connect to Outreach Dashboard API. Please check your internet connection.'
        }
    except Exception as e:
        current_app.logger.error(f"Error fetching Outreach Dashboard data: {str(e)}")
        return {
            'success': False,
            'data': None,
            'error': f'Unexpected error: {str(e)}'
        }


def fetch_course_data(base_url: str) -> Dict[str, Any]:
    """
    Fetch course data from Outreach Dashboard API.
    
    Args:
        base_url: Base URL of the course (without /course.json)
        
    Returns:
        Dictionary with keys:
            - 'success': Boolean indicating if fetch was successful
            - 'data': Course data dictionary if successful (None otherwise)
            - 'error': Error message if failed (None if successful)
    """
    if not base_url or not isinstance(base_url, str):
        return {
            'success': False,
            'data': None,
            'error': 'Base URL is required'
        }
    
    base_url = base_url.strip()
    
    # Remove common suffixes that users might include
    # This handles cases like /home, /enroll, /course.json, etc.
    common_suffixes = ['/home', '/enroll', '/course.json', '/students', '/articles', '/timeline']
    for suffix in common_suffixes:
        if base_url.endswith(suffix):
            base_url = base_url[:-len(suffix)]
            break
    
    base_url = base_url.rstrip('/')
    
    # Parse URL to get school and course_slug
    parsed = parse_outreach_url(base_url)
    if not parsed['valid']:
        return {
            'success': False,
            'data': None,
            'error': 'Invalid Outreach Dashboard URL format'
        }
    
    # Build API URL using helper function
    api_url = _build_api_url(parsed['school'], parsed['course_slug'], 'course.json')
    
    # Make API request using base handler
    result = _make_api_request(api_url)
    
    if not result['success']:
        return result
    
    # Extract course data from response
    data = result['data']
    if 'course' in data:
        return {
            'success': True,
            'data': data['course'],
            'error': None
        }
    else:
        return {
            'success': False,
            'data': None,
            'error': 'Invalid API response format: missing "course" key'
        }


def fetch_course_users(base_url: str) -> Dict[str, Any]:
    """
    Fetch course users data from Outreach Dashboard API.
    
    Returns an array of user objects with enrollment details, contribution metrics,
    and links to Wikimedia profiles.
    
    Args:
        base_url: Base URL of the course (without /users.json)
        
    Returns:
        Dictionary with keys:
            - 'success': Boolean indicating if fetch was successful
            - 'data': List of user objects if successful (None otherwise)
            - 'error': Error message if failed (None if successful)
            
    User objects include important fields:
        - id: Unique Wikimedia user ID
        - username: Wikimedia username
        - role: User's role (0 for student, 1 for instructor)
        - enrolled_at: Enrollment timestamp (ISO 8601)
        - character_sum_ms: Characters added to mainspace
        - character_sum_us: Characters added to userspace
        - total_uploads: Number of files uploaded
        - contribution_url: URL to user's contributions
        - sandbox_url: URL to user's sandbox
        - global_contribution_url: URL to global contributions
        - admin: Boolean indicating admin rights
    """
    if not base_url or not isinstance(base_url, str):
        return {
            'success': False,
            'data': None,
            'error': 'Base URL is required'
        }
    
    base_url = base_url.strip()
    
    # Remove common suffixes that users might include
    common_suffixes = ['/home', '/enroll', '/users.json', '/course.json', '/students', '/articles', '/timeline']
    for suffix in common_suffixes:
        if base_url.endswith(suffix):
            base_url = base_url[:-len(suffix)]
            break
    
    base_url = base_url.rstrip('/')
    
    # Parse URL to get school and course_slug
    parsed = parse_outreach_url(base_url)
    if not parsed['valid']:
        return {
            'success': False,
            'data': None,
            'error': 'Invalid Outreach Dashboard URL format'
        }
    
    # Build API URL using helper function
    api_url = _build_api_url(parsed['school'], parsed['course_slug'], 'users.json')
    
    # Make API request using base handler
    result = _make_api_request(api_url)
    
    if not result['success']:
        return result
    
    # Extract users data from response
    # Response structure: {'course': {'users': [...]}}
    data = result['data']
    if 'course' in data and 'users' in data['course']:
        users = data['course']['users']
        # Ensure it's a list (API may return empty array)
        if isinstance(users, list):
            return {
                'success': True,
                'data': users,
                'error': None
            }
        else:
            return {
                'success': False,
                'data': None,
                'error': 'Invalid API response format: "users" is not an array'
            }
    else:
        return {
            'success': False,
            'data': None,
            'error': 'Invalid API response format: missing "course.users" key'
        }


def build_course_api_url(base_url: str) -> Optional[str]:
    """
    Build the full API URL from a base URL.
    
    Args:
        base_url: Base URL of the course
        
    Returns:
        Full API URL or None if base_url is invalid
    """
    parsed = parse_outreach_url(base_url)
    if not parsed['valid']:
        return None
    
    return f"{OUTREACH_DASHBOARD_BASE}/courses/{parsed['school']}/{parsed['course_slug']}/course.json"

