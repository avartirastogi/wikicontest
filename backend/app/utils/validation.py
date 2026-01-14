"""Input validation utilities for security and data integrity."""

MAX_USERNAME_LENGTH = 50
MAX_EMAIL_LENGTH = 255
MAX_CONTEST_NAME_LENGTH = 200
MAX_PROJECT_NAME_LENGTH = 100
MAX_DESCRIPTION_LENGTH = 5000
MAX_URL_LENGTH = 2048
MAX_COMMENT_LENGTH = 2000
MAX_CATEGORY_COUNT = 50


def validate_string_length(value, field_name, max_length, min_length=0):
    """
    Validate that a string is within allowed length limits.
    
    Args:
        value: String value to validate
        field_name: Name of the field (for error messages)
        max_length: Maximum allowed length
        min_length: Minimum allowed length (default: 0)
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not isinstance(value, str):
        return False, f'{field_name} must be a string'

    if len(value) < min_length:
        return False, f'{field_name} must be at least {min_length} characters'

    if len(value) > max_length:
        return False, f'{field_name} must be at most {max_length} characters'

    return True, None


def validate_username_length(username):
    """
    Validate username length.
    
    Args:
        username: Username string to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    return validate_string_length(
        username, 'Username', MAX_USERNAME_LENGTH, min_length=3
    )


def validate_email_length(email):
    """
    Validate email length.
    
    Args:
        email: Email string to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    return validate_string_length(
        email, 'Email', MAX_EMAIL_LENGTH, min_length=5
    )


# REMOVED: validate_password_length - password-based authentication removed
# Authentication is now exclusively via MediaWiki OAuth


def validate_contest_name_length(name):
    """
    Validate contest name length.
    
    Args:
        name: Contest name string to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    return validate_string_length(
        name, 'Contest name', MAX_CONTEST_NAME_LENGTH, min_length=1
    )


def validate_project_name_length(project_name):
    """
    Validate project name length.
    
    Args:
        project_name: Project name string to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    return validate_string_length(
        project_name, 'Project name', MAX_PROJECT_NAME_LENGTH, min_length=1
    )


def validate_description_length(description):
    """
    Validate description length.
    
    Args:
        description: Description string to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if description is None:
        return True, None

    return validate_string_length(
        description, 'Description', MAX_DESCRIPTION_LENGTH, min_length=0
    )


def validate_url_length(url):
    """
    Validate URL length.
    
    Args:
        url: URL string to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    return validate_string_length(
        url, 'URL', MAX_URL_LENGTH, min_length=1
    )


def validate_comment_length(comment):
    """
    Validate comment/review comment length.
    
    Args:
        comment: Comment string to validate
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if comment is None:
        return True, None

    return validate_string_length(
        comment, 'Comment', MAX_COMMENT_LENGTH, min_length=0
    )


def validate_category_list(categories):
    """
    Validate category list length and individual URLs.
    
    Args:
        categories: List of category URLs
    
    Returns:
        tuple: (is_valid: bool, error_message: str or None)
    """
    if not isinstance(categories, list):
        return False, 'Categories must be a list'

    if len(categories) > MAX_CATEGORY_COUNT:
        return False, f'Maximum {MAX_CATEGORY_COUNT} categories allowed'

    # Validate each category URL length
    for i, category in enumerate(categories):
        if not isinstance(category, str):
            return False, f'Category {i+1} must be a string'

        is_valid, error = validate_url_length(category)
        if not is_valid:
            return False, f'Category {i+1}: {error}'

    return True, None
