"""
Contest Model for WikiContest Application
Defines the Contest table and related functionality
"""

import json
from datetime import datetime, date

from app.database import db
from app.models.base_model import BaseModel


class Contest(BaseModel):
    """
    Contest model representing contests in the WikiContest platform

    Attributes:
        id: Primary key, auto-incrementing integer
        name: Name of the contest
        project_name: Name of the associated project (e.g., 'Wikimedia')
        created_by: Username of the user who created the contest
        description: Description of the contest
        start_date: Start date of the contest
        end_date: End date of the contest
        rules: JSON string containing contest rules
        marks_setting_accepted: Points awarded for accepted submissions
        marks_setting_rejected: Points awarded for rejected submissions
        jury_members: Comma-separated list of jury member usernames
        created_at: Timestamp when contest was created
    """

    __tablename__ = "contests"

    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Contest basic information
    name = db.Column(db.String(200), nullable=False)
    project_name = db.Column(db.String(100), nullable=False)

    # Contest creator (foreign key to users.username)
    created_by = db.Column(
        db.String(50), db.ForeignKey("users.username"), nullable=False
    )

    # Contest details
    description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.Date, nullable=True)
    end_date = db.Column(db.Date, nullable=True)

    # Contest rules and scoring
    rules = db.Column(db.Text, nullable=True)  # JSON string
    marks_setting_accepted = db.Column(db.Integer, default=0, nullable=False)
    marks_setting_rejected = db.Column(db.Integer, default=0, nullable=False)
    allowed_submission_type = db.Column(db.String(20), default="both", nullable=False)

    # Byte count requirement for article submissions
    # Articles must have byte count at least min_byte_count
    min_byte_count = db.Column(db.Integer, nullable=False)  # Minimum byte count (required)

    # MediaWiki category URLs (JSON array)
    # Required categories that articles must belong to
    categories = db.Column(db.Text, nullable=False, default='[]')  # JSON array of category URLs

    # Jury members (comma-separated usernames)
    jury_members = db.Column(db.Text, nullable=True)

    # Template link for contest (URL to Wiki template page)
    # Used to enforce template attachment on submitted articles
    template_link = db.Column(db.Text, nullable=True)

    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    submissions = db.relationship(
        "Submission", back_populates="contest", lazy="dynamic"
    )

    def __init__(self, name, project_name, created_by, **kwargs):
        """
        Initialize a new Contest instance

        Args:
            name: Name of the contest
            project_name: Name of the associated project
            created_by: Username of the creator
            **kwargs: Additional contest attributes
        """
        self.name = name
        self.project_name = project_name
        self.created_by = created_by

        # Set optional attributes
        self.description = kwargs.get("description")
        self.start_date = kwargs.get("start_date")
        self.end_date = kwargs.get("end_date")
        self.marks_setting_accepted = kwargs.get("marks_setting_accepted", 0)
        self.marks_setting_rejected = kwargs.get("marks_setting_rejected", 0)
        self.allowed_submission_type = kwargs.get("allowed_submission_type", "both")

        # Byte count requirement (required)
        # Articles must have byte count at least this value
        self.min_byte_count = kwargs.get('min_byte_count', 0)

        # Handle categories (list of category URLs)
        self.set_categories(kwargs.get("categories", []))

        # Handle rules and jury_members
        self.set_rules(kwargs.get("rules", {}))
        self.set_jury_members(kwargs.get("jury_members", []))

        # Template link for contest template enforcement
        self.template_link = kwargs.get("template_link")

    def set_rules(self, rules_dict):
        """
        Set contest rules from dictionary

        Args:
            rules_dict: Dictionary containing contest rules
        """
        if isinstance(rules_dict, dict):
            self.rules = json.dumps(rules_dict)
        else:
            self.rules = json.dumps({})

    def get_rules(self):
        """
        Get contest rules as dictionary

        Returns:
            dict: Contest rules dictionary
        """
        if self.rules:
            try:
                return json.loads(self.rules)
            except json.JSONDecodeError:
                return {}
        return {}

    def set_jury_members(self, jury_list):
        """
        Set jury members from list

        Args:
            jury_list: List of jury member usernames
        """
        if isinstance(jury_list, list):
            self.jury_members = ",".join(jury_list)
        else:
            self.jury_members = ""

    def get_jury_members(self):
        """
        Get jury members as list

        Returns:
            list: List of jury member usernames
        """
        if self.jury_members:
            return [
                username.strip()
                for username in self.jury_members.split(",")
                if username.strip()
            ]
        return []

    def set_categories(self, categories_list):
        """
        Set contest categories from list

        Args:
            categories_list: List of category URLs
        """
        if isinstance(categories_list, list):
            self.categories = json.dumps(categories_list)
        else:
            self.categories = json.dumps([])

    def get_categories(self):
        """
        Get contest categories as list

        Returns:
            list: List of category URLs
        """
        if self.categories:
            try:
                return json.loads(self.categories)
            except json.JSONDecodeError:
                return []
        return []

    def validate_byte_count(self, byte_count):
        """
        Validate if article byte count meets the contest's minimum requirement

        Args:
            byte_count: Article byte count to validate (can be None)

        Returns:
            tuple: (is_valid: bool, error_message: str or None)
                  Returns (True, None) if valid, (False, error_message) if invalid
        """
        # If byte count is None, we can't validate it
        # This might happen if MediaWiki API fails to fetch the size
        if byte_count is None:
            return False, 'Article byte count could not be determined. Please ensure the article exists and try again.'

        # Check minimum byte count (always required)
        if byte_count < self.min_byte_count:
            return False, f'Article byte count ({byte_count}) is below the minimum required ({self.min_byte_count} bytes)'

        # Byte count meets the requirement
        return True, None

    def is_active(self):
        """
        Check if contest is currently active

        Returns:
            bool: True if contest is active, False otherwise
        """
        if not self.start_date or not self.end_date:
            return False

        today = date.today()
        return self.start_date <= today <= self.end_date

    def is_upcoming(self):
        """
        Check if contest is upcoming

        Returns:
            bool: True if contest is upcoming, False otherwise
        """
        if not self.start_date:
            return False

        today = date.today()
        return self.start_date > today

    def is_past(self):
        """
        Check if contest is past

        Returns:
            bool: True if contest is past, False otherwise
        """
        if not self.end_date:
            return False

        today = date.today()
        return self.end_date < today

    def get_status(self):
        """
        Get contest status

        Returns:
            str: Contest status ('current', 'upcoming', 'past', or 'unknown')
        """
        if self.is_active():
            return "current"
        if self.is_upcoming():
            return "upcoming"
        if self.is_past():
            return "past"
        return "unknown"

    def get_submission_count(self):
        """
        Get number of submissions for this contest

        Returns:
            int: Number of submissions
        """
        return self.submissions.count()

    def get_leaderboard(self):
        """
        Get leaderboard for this contest

        Returns:
            list: List of users with their scores, sorted by score descending
        """
        # Import here to avoid circular imports
        from app.models.user import User
        from app.models.submission import Submission

        # Query to get user scores for this contest
        leaderboard_query = (
            db.session.query(
                User.id,
                User.username,
                db.func.sum(Submission.score).label("total_score"),
            )
            .join(Submission)
            .filter(Submission.contest_id == self.id)
            .group_by(User.id, User.username)
            .order_by(db.func.sum(Submission.score).desc())
            .all()
        )

        return [
            {
                "user_id": row.id,
                "username": row.username,
                "total_score": row.total_score or 0,
            }
            for row in leaderboard_query
        ]

    def to_dict(self):
        """
        Convert contest instance to dictionary for JSON serialization

        Returns:
            dict: Contest data
        """
        return {
            'id': self.id,
            'name': self.name,
            'project_name': self.project_name,
            'created_by': self.created_by,
            'description': self.description,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'rules': self.get_rules(),
            'marks_setting_accepted': self.marks_setting_accepted,
            'marks_setting_rejected': self.marks_setting_rejected,
            'allowed_submission_type': self.allowed_submission_type,
            'min_byte_count': self.min_byte_count,
            'categories': self.get_categories(),
            'jury_members': self.get_jury_members(),
            'template_link': self.template_link,
            # Format datetime as ISO string with 'Z' suffix to indicate UTC
            # This ensures JavaScript interprets it as UTC, not local time
            "created_at": (
                (self.created_at.isoformat() + "Z") if self.created_at else None
            ),
            "submission_count": self.get_submission_count(),
            "status": self.get_status(),
        }

    def __repr__(self):
        """String representation of Contest instance"""
        return f"<Contest {self.name}>"
