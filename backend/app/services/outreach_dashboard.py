"""
Outreach Dashboard API Service

This module provides functions to interact with Wikimedia's Outreach Dashboard API.
It handles URL parsing, validation, and fetching course data.
"""

import re
from typing import Dict, Optional, Any
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
    
    # Pattern: /courses/{school}/{course_slug} or /courses/{school}/{course_slug}/course.json
    pattern = r'^courses/([^/]+)/([^/]+)(?:/course\.json)?/?$'
    match = re.match(pattern, path)
    
    if match:
        school = match.group(1)
        course_slug = match.group(2)
        return {
            'school': school,
            'course_slug': course_slug,
            'valid': True
        }
    
    return {'school': None, 'course_slug': None, 'valid': False}


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
    
    # Ensure base_url doesn't end with /course.json
    if base_url.endswith('/course.json'):
        base_url = base_url[:-12]
    base_url = base_url.rstrip('/')
    
    # Parse URL to get school and course_slug
    parsed = parse_outreach_url(base_url)
    if not parsed['valid']:
        return {
            'success': False,
            'data': None,
            'error': 'Invalid Outreach Dashboard URL format'
        }
    
    # Build API URL
    api_url = f"{OUTREACH_DASHBOARD_BASE}/courses/{parsed['school']}/{parsed['course_slug']}/course.json"
    
    try:
        # Make request to Outreach Dashboard API
        response = requests.get(api_url, timeout=API_TIMEOUT)
        
        if response.status_code == 404:
            return {
                'success': False,
                'data': None,
                'error': 'Course not found. Please verify the URL is correct.'
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
        
        # Extract course data from response
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
                'error': 'Invalid API response format'
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

