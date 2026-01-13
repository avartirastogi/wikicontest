"""
Utility Functions for WikiContest Application.

This module contains shared helpers that are used by the Flask routes,
Alembic‑backed models, and maintenance scripts.

The focus here is small, well‑documented functions:
- Permission and access control helpers.
- MediaWiki API helpers.
- Simple parsing helpers.

All functions are intentionally simple and safe.
They catch network / parsing errors and return `None` instead of crashing.
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Dict, Iterable, List, Optional
from urllib.parse import urlparse, unquote, parse_qs

import requests
from flask import jsonify


__all__ = [
    "validate_contest_submission_access",
    "get_article_size_at_timestamp",
    "extract_page_title_from_url",
    "get_latest_revision_author",
    "build_mediawiki_revisions_api_params",
    "get_mediawiki_headers",
    "get_article_reference_count",
]


# ------------------------------------------------------------------------
# ACCESS CONTROL HELPERS
# ------------------------------------------------------------------------

def validate_contest_submission_access(contest_id, user, Contest):  # pylint: disable=invalid-name
    # pylint: disable=invalid-name
    """
    Check if a user is allowed to view or manage submissions for a contest.

    This is used by multiple routes and must stay very small and clear.

    Returns:
        (contest, error_response)
        - contest: Contest object when access is allowed, else None.
        - error_response: (Response, status_code) when access is denied, else None.
    """
    # Fetch contest from the database
    contest = Contest.query.get(contest_id)

    if not contest:
        # Contest does not exist
        return None, (jsonify({"error": "Contest not found"}), 404)

    # --- Permission Check: Admin ---
    # Admin users are always allowed
    # Our User model exposes this as a method (see app.models.user.User)
    if hasattr(user, "is_admin") and callable(getattr(user, "is_admin")):
        if user.is_admin():
            return contest, None

    # --- Permission Check: Contest Creator ---
    # Contest creator is allowed
    # created_by stores the creator's username
    if getattr(user, "username", None) == getattr(contest, "created_by", None):
        return contest, None

    # --- Permission Check: Jury Member ---
    # Jury members are allowed
    # Contest keeps jury members as a comma‑separated string of usernames
    try:
        from app.models.user import User  # local import to avoid circular deps
    except Exception:  # pylint: disable=broad-exception-caught
        User = None  # type: ignore  # pylint: disable=invalid-name

    if User is not None and hasattr(user, "is_jury_member"):
        try:
            # Prefer the dedicated helper on the User model
            if user.is_jury_member(contest):
                return contest, None
        except Exception:  # pylint: disable=broad-exception-caught
            # Fall back to manual parsing if something goes wrong
            pass

    # Manual fallback: parse jury_members as usernames list
    jury_members_raw = getattr(contest, "jury_members", "") or ""
    jury_usernames = [u.strip() for u in jury_members_raw.split(",") if u.strip()]
    if getattr(user, "username", None) in jury_usernames:
        return contest, None

    # No matching permission rule → deny access
    return None, (jsonify({"error": "Permission denied"}), 403)


# ------------------------------------------------------------------------
# MEDIAWIKI API HELPERS
# ------------------------------------------------------------------------

def extract_page_title_from_url(article_url: str) -> Optional[str]:
    """
    Extract a MediaWiki page title from a full article URL.

    This mirrors the logic used in the maintenance scripts.
    It supports:
    - `/wiki/Page_Title` style URLs.
    - `/w/index.php?title=Page_Title` style URLs.
    - Fallback to the last path segment.

    Returns:
        The decoded page title string, or None when it cannot be extracted.
    """
    if not article_url:
        return None

    url_obj = urlparse(article_url)

    # Standard `/wiki/Page_Title` format (most common)
    if "/wiki/" in url_obj.path:
        return unquote(url_obj.path.split("/wiki/")[1])

    # Old style `/w/index.php?title=Page_Title` format
    if "title=" in url_obj.query:
        query_params = parse_qs(url_obj.query)
        return unquote(query_params.get("title", [""])[0])

    # Fallback: last non‑empty path segment
    parts = [p for p in url_obj.path.split("/") if p]
    if parts:
        return unquote(parts[-1])

    return None


def build_mediawiki_revisions_api_params(page_title: str) -> Dict[str, Any]:  # pylint: disable=invalid-name
    """
    Build a standard parameter set for MediaWiki `revisions` queries.

    This is shared by the routes and scripts so that any change to the
    API contract is done in a single place.
    """
    return {
        "action": "query",
        "titles": page_title,
        "format": "json",
        "formatversion": "2",  # Use modern API format (array-based pages)
        "prop": "info|revisions",
        # We request timestamp, user, userid, and size so that callers can
        # compute authorship and word/byte counts
        "rvprop": "timestamp|user|userid|comment|size",
        # Get both newest and oldest revisions in a tiny window
        "rvlimit": "2",
        # With rvdir='older', the first revision in the list is the newest
        "rvdir": "older",
        # Follow redirects to get the actual page
        "redirects": "true",
        # Convert titles to the preferred variant
        "converttitles": "true",
    }


def get_mediawiki_headers() -> Dict[str, str]:
    """
    Return a standard set of HTTP headers for MediaWiki API calls.

    MediaWiki requires a descriptive User‑Agent.
    Using one shared helper keeps this string consistent.
    """
    return {
        "User-Agent": (
            "WikiContest/1.0 (https://wikicontest.toolforge.org; "
            "contact@wikicontest.org) Python/requests"
        )
    }


def get_latest_revision_author(revisions: Iterable[Dict[str, Any]]) -> Optional[str]:
    """
    Get the author of the latest revision from a revisions list.

    The calling code usually passes the list returned by the MediaWiki API.
    With `rvdir='older'`, the first element is the newest revision.

    Returns:
        Username string when available, a simple "User ID: <id>" fallback,
        or None when no author information is present.
    """
    revisions_list: List[Dict[str, Any]] = list(revisions or [])
    if not revisions_list:
        return None

    # First element is the newest revision (with rvdir='older')
    latest = revisions_list[0]

    # Prefer the human‑readable username when available
    user_name = latest.get("user")
    if user_name:
        return user_name

    # Fallback to numeric user id when username is missing
    # This can happen for deleted/suppressed users
    user_id = latest.get("userid")
    if user_id:
        return f"User ID: {user_id}"

    return None


def get_article_size_at_timestamp(article_url: str, when: datetime) -> Optional[int]:
    """
    Get the article size (bytes) at or before a specific timestamp.

    This is used to compute expansion bytes for contests.
    It keeps the logic small by doing a single `revisions` API call and
    returning the size of the newest revision that is not newer than `when`.

    Args:
        article_url: Full article URL.
        when: UTC datetime to look back from.

    Returns:
        Integer byte size if available, otherwise None.
    """
    # Extract page title from URL
    page_title = extract_page_title_from_url(article_url)
    if not page_title:
        return None

    # Build API endpoint URL
    url_obj = urlparse(article_url)
    base_url = f"{url_obj.scheme}://{url_obj.netloc}"
    api_url = f"{base_url}/w/api.php"

    # ISO timestamp in the format expected by MediaWiki
    when_iso = when.strftime("%Y-%m-%dT%H:%M:%SZ")

    # Build API parameters for historical size query
    params: Dict[str, Any] = {
        "action": "query",
        "titles": page_title,
        "format": "json",
        "formatversion": "2",
        "prop": "revisions",
        "rvprop": "timestamp|size",
        # We want the newest revision at or before `when`
        "rvlimit": "1",
        "rvdir": "older",  # Start from newest and go back in time
        "rvstart": when_iso,  # Start at this timestamp
        "redirects": "true",
        "converttitles": "true",
    }

    try:
        response = requests.get(api_url, params=params, headers=get_mediawiki_headers(), timeout=10)
    except requests.RequestException:
        # Network error. Caller will handle `None` gracefully
        return None

    if response.status_code != 200:
        return None

    try:
        data = response.json()
    except ValueError:
        # Invalid JSON response
        return None

    if "error" in data:
        # API returned an error
        return None

    # Extract page data from response
    pages = data.get("query", {}).get("pages", [])
    if not pages:
        return None

    page_data = pages[0]
    revisions = page_data.get("revisions", [])
    if not revisions:
        # No revisions found at or before the timestamp
        return None

    # Single revision because we requested `rvlimit=1`
    rev = revisions[0]
    return rev.get("size")


def _count_footnotes_from_content(article_content: str) -> int:
    """
    Count footnote references (<ref> tags) in article content.

    Args:
        article_content: Raw article content from MediaWiki API

    Returns:
        Integer count of <ref> tags found
    """
    if not article_content:
        return 0
    ref_pattern = r'<ref\b'
    ref_matches = re.findall(ref_pattern, article_content, re.IGNORECASE)
    return len(ref_matches)


def _extract_article_content_from_revision(latest_rev: dict) -> str:  # pylint: disable=invalid-name
    """
    Extract article content from MediaWiki revision data.

    Args:
        latest_rev: Revision data from MediaWiki API

    Returns:
        Article content string, or empty string if not found
    """
    # Try to get content from slots.main.*
    slots = latest_rev.get("slots", {})
    if slots:
        main_slot = slots.get("main", {})
        article_content = main_slot.get("*", "") or main_slot.get("content", "")
        if article_content:
            return article_content

    # Fallback to direct content access
    return latest_rev.get("*", "") or latest_rev.get("content", "")


def _fetch_footnotes_count(api_url: str, page_title: str, headers: dict) -> int:
    """
    Fetch and count footnotes from article content.

    Args:
        api_url: MediaWiki API URL
        page_title: Article page title
        headers: HTTP headers for API request

    Returns:
        Integer count of footnotes, or 0 if fetch fails
    """
    try:
        rev_params = {
            "action": "query",
            "titles": page_title,
            "format": "json",
            "formatversion": "2",
            "prop": "revisions",
            "rvprop": "ids|content",
            "rvlimit": "1",
            "rvdir": "older",
            "redirects": "true",
            "converttitles": "true",
            "rvslots": "*",
        }

        rev_response = requests.get(
            api_url, params=rev_params, headers=headers, timeout=10
        )

        if rev_response.status_code != 200:
            return 0

        rev_data = rev_response.json()
        if "error" in rev_data:
            return 0

        pages = rev_data.get("query", {}).get("pages", [])
        if not pages:
            return 0

        page_data = pages[0]
        if page_data.get("missing", False):
            return 0

        revisions = page_data.get("revisions", [])
        if not revisions:
            return 0

        latest_rev = revisions[0]
        article_content = _extract_article_content_from_revision(latest_rev)
        return _count_footnotes_from_content(article_content)

    except Exception:  # pylint: disable=broad-exception-caught
        # If footnote counting fails, continue with external links only
        # This ensures we still return a count even if content fetch fails
        return 0


def get_article_reference_count(article_url: str) -> Optional[int]:
    """
    Get the total number of references in a MediaWiki article.
    
    Counts both:
    1. Footnotes (<ref> tags) - by parsing article content
    2. External links (URLs) - using MediaWiki extlinks API
    
    Uses the latest revision to ensure accuracy. Handles pagination
    automatically for articles with >500 external links.

    Args:
        article_url: Full URL to the article

    Returns:
        Integer count of total references (footnotes + external links) if successful,
        None if fetch fails.
    """
    try:
        # Extract page title from URL using shared utility
        page_title = extract_page_title_from_url(article_url)
        if not page_title:
            return None

        # Parse URL to get base URL
        url_obj = urlparse(article_url)
        base_url = f"{url_obj.scheme}://{url_obj.netloc}"
        api_url = f"{base_url}/w/api.php"
        headers = get_mediawiki_headers()

        # Step 1: Get article content to count footnotes (<ref> tags)
        footnotes_count = _fetch_footnotes_count(api_url, page_title, headers)

        # Step 2: Count external links using extlinks API
        external_links_count = 0
        elcontinue = None

        # Loop to handle pagination (MediaWiki API returns max 500 links per request)
        while True:
            # Build API parameters for external links query
            # Use prop=extlinks to get all external URLs (not interwikis)
            api_params = {
                "action": "query",
                "titles": page_title,
                "format": "json",
                "formatversion": "2",
                "prop": "extlinks",
                "ellimit": "500",  # Maximum allowed per request
                "redirects": "true",
                "converttitles": "true",
            }

            # Add continuation token if we're paginating
            if elcontinue:
                api_params["elcontinue"] = elcontinue

            # Make API request using shared headers
            response = requests.get(
                api_url, params=api_params, headers=headers, timeout=10
            )

            if response.status_code != 200:
                # Request failed, return None
                return None

            api_data = response.json()

            # Check for API errors
            if "error" in api_data:
                return None

            # Extract pages from response
            pages = api_data.get("query", {}).get("pages", [])
            if not pages or len(pages) == 0:
                return None

            page_data = pages[0]

            # Check if page exists (not a missing/deleted page)
            if page_data.get("missing", False):
                return None

            # Count external links in this batch
            extlinks = page_data.get("extlinks", [])
            external_links_count += len(extlinks)

            # Check if there are more links to fetch (pagination)
            continue_info = api_data.get("continue", {})
            elcontinue = continue_info.get("elcontinue")

            # If no continuation token, we've fetched all links
            if not elcontinue:
                break

        # Return total count: footnotes + external links
        total_count = footnotes_count + external_links_count
        return total_count

    except Exception as error:  # pylint: disable=broad-exception-caught
        # Log error but don't fail
        # This ensures the application continues even if reference counting fails
        try:
            from flask import current_app
            current_app.logger.warning(
                f"Failed to fetch reference count: {str(error)}"
            )
        except Exception:  # pylint: disable=broad-exception-caught
            # Logging itself failed, silently continue
            pass
        return None
