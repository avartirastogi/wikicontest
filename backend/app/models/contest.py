"""
Contest Model for WikiContest Application
Defines the Contest table and related functionality
"""

import json
from datetime import datetime, date

from app.database import db
from app.models.base_model import BaseModel


# ------------------------------------------------------------------------
# CONTEST MODEL
# ------------------------------------------------------------------------

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


    # ------------------------------------------------------------------------
    # Database Columns - Core Fields
    # ------------------------------------------------------------------------

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


    # ------------------------------------------------------------------------
    # Database Columns - Scoring & Rules
    # ------------------------------------------------------------------------

    # Contest rules (stored as JSON string)
    rules = db.Column(db.Text, nullable=True)

    # Simple scoring: fixed points for accepted/rejected submissions
    marks_setting_accepted = db.Column(db.Integer, default=0, nullable=False)
    marks_setting_rejected = db.Column(db.Integer, default=0, nullable=False)

    # Multi-parameter scoring configuration (stored as JSON string)
    scoring_parameters = db.Column(db.Text, nullable=True)

    # Submission type restriction: 'new', 'expansion', or 'both'
    allowed_submission_type = db.Column(db.String(20), default="both", nullable=False)


    # ------------------------------------------------------------------------
    # Database Columns - Article Requirements
    # ------------------------------------------------------------------------

    # Minimum byte count required for article submissions
    min_byte_count = db.Column(db.Integer, nullable=False)

    # Minimum reference count (external links) required for submissions
    # Default 0 means no requirement
    min_reference_count = db.Column(db.Integer, nullable=False, default=0)

    # Required MediaWiki categories (stored as JSON array of URLs)
    # Articles must belong to at least one of these categories
    categories = db.Column(db.Text, nullable=False, default="[]")


    # ------------------------------------------------------------------------
    # Database Columns - People Management
    # ------------------------------------------------------------------------

    # Jury members who can review submissions (comma-separated usernames)
    jury_members = db.Column(db.Text, nullable=True)

    # Contest organizers who can manage the contest (comma-separated usernames)
    # Creator is always included as an organizer
    organizers = db.Column(db.Text, nullable=True)


    # ------------------------------------------------------------------------
    # Database Columns - Metadata
    # ------------------------------------------------------------------------

    # Timestamp when contest was created (UTC)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


    # ------------------------------------------------------------------------
    # Relationships
    # ------------------------------------------------------------------------

    # One-to-many: Contest has many submissions
    # lazy='dynamic' returns a query object instead of loading all submissions
    submissions = db.relationship(
        "Submission", back_populates="contest", lazy="dynamic"
    )


    # ------------------------------------------------------------------------
    # INITIALIZATION
    # ------------------------------------------------------------------------

    def __init__(self, name, project_name, created_by, **kwargs):
        """
        Initialize a new Contest instance

        Args:
            name: Name of the contest
            project_name: Name of the associated project
            created_by: Username of the creator
            **kwargs: Additional contest attributes
        """
        # Set required fields
        self.name = name
        self.project_name = project_name
        self.created_by = created_by

        # Set optional basic attributes with defaults
        self.description = kwargs.get("description")
        self.start_date = kwargs.get("start_date")
        self.end_date = kwargs.get("end_date")
        self.marks_setting_accepted = kwargs.get("marks_setting_accepted", 0)
        self.marks_setting_rejected = kwargs.get("marks_setting_rejected", 0)
        self.allowed_submission_type = kwargs.get("allowed_submission_type", "both")

        # Set scoring configuration (handles validation internally)
        self.set_scoring_parameters(kwargs.get("scoring_parameters"))

        # Set article requirements
        self.min_byte_count = kwargs.get("min_byte_count", 0)
        self.min_reference_count = kwargs.get("min_reference_count", 0)

        # Set complex fields using setter methods (handle JSON/list conversion)
        self.set_categories(kwargs.get("categories", []))
        self.set_rules(kwargs.get("rules", {}))
        self.set_jury_members(kwargs.get("jury_members", []))

        # Set organizers (creator is automatically added)
        self.set_organizers(kwargs.get("organizers", []), created_by)


    # ------------------------------------------------------------------------
    # RULES MANAGEMENT (JSON Storage)
    # ------------------------------------------------------------------------

    def set_rules(self, rules_dict):
        """
        Set contest rules from dictionary

        Args:
            rules_dict: Dictionary containing contest rules
        """
        # Convert dictionary to JSON string for database storage
        if isinstance(rules_dict, dict):
            self.rules = json.dumps(rules_dict)
        else:
            # Fallback to empty rules if invalid input
            self.rules = json.dumps({})


    def get_rules(self):
        """
        Get contest rules as dictionary

        Returns:
            dict: Contest rules dictionary
        """
        if self.rules:
            try:
                # Parse JSON string back to dictionary
                return json.loads(self.rules)
            except json.JSONDecodeError:
                # Return empty dict if JSON is corrupted
                return {}
        return {}


    # ------------------------------------------------------------------------
    # JURY MEMBERS MANAGEMENT (Comma-Separated Storage)
    # ------------------------------------------------------------------------

    def set_jury_members(self, jury_list):
        """
        Set jury members from list

        Args:
            jury_list: List of jury member usernames
        """
        # Convert list to comma-separated string for database storage
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
            # Parse comma-separated string back to list
            # Strip whitespace and filter empty strings
            return [
                username.strip()
                for username in self.jury_members.split(",")
                if username.strip()
            ]
        return []


    # ------------------------------------------------------------------------
    # CATEGORIES MANAGEMENT (JSON Array Storage)
    # ------------------------------------------------------------------------

    def set_categories(self, categories_list):
        """
        Set contest categories from list

        Args:
            categories_list: List of category URLs
        """
        # Convert list to JSON array string for database storage
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
                # Parse JSON array string back to list
                return json.loads(self.categories)
            except json.JSONDecodeError:
                # Return empty list if JSON is corrupted
                return []
        return []


    # ------------------------------------------------------------------------
    # ARTICLE VALIDATION
    # ------------------------------------------------------------------------

    def validate_byte_count(self, byte_count):
        """
        Validate if article byte count meets the contest's minimum requirement

        Args:
            byte_count: Article byte count to validate (can be None)

        Returns:
            tuple: (is_valid: bool, error_message: str or None)
                  Returns (True, None) if valid, (False, error_message) if invalid
        """
        # Handle case where MediaWiki API failed to fetch article size
        if byte_count is None:
            return (
                False,
                "Article byte count could not be determined. Please ensure the article exists and try again.",
            )

        # Validate against minimum requirement (always enforced)
        if byte_count < self.min_byte_count:
            return (
                False,
                f"Article byte count ({byte_count}) is below the minimum required ({self.min_byte_count} bytes)",
            )

        # Validation passed
        return True, None

    # ------------------------------------------------------------------------
    # CONTEST STATUS CHECKS
    # ------------------------------------------------------------------------

    def is_active(self):
        """
        Check if contest is currently active

        Returns:
            bool: True if contest is active, False otherwise
        """
        # Cannot be active without dates
        if not self.start_date or not self.end_date:
            return False

        # Check if today falls within contest period
        today = date.today()
        return self.start_date <= today <= self.end_date


    def is_upcoming(self):
        """
        Check if contest is upcoming

        Returns:
            bool: True if contest is upcoming, False otherwise
        """
        # Cannot be upcoming without start date
        if not self.start_date:
            return False

        # Check if start date is in the future
        today = date.today()
        return self.start_date > today


    def is_past(self):
        """
        Check if contest is past

        Returns:
            bool: True if contest is past, False otherwise
        """
        # Cannot be past without end date
        if not self.end_date:
            return False

        # Check if end date has passed
        today = date.today()
        return self.end_date < today


    def get_status(self):
        """
        Get contest status

        Returns:
            str: Contest status ('current', 'upcoming', 'past', or 'unknown')
        """
        # Determine status based on date checks
        if self.is_active():
            return "current"
        if self.is_upcoming():
            return "upcoming"
        if self.is_past():
            return "past"
        # Fallback for contests without proper dates
        return "unknown"


    # ------------------------------------------------------------------------
    # STATISTICS & QUERIES
    # ------------------------------------------------------------------------

    def get_submission_count(self):
        """
        Get number of submissions for this contest

        Returns:
            int: Number of submissions
        """
        # Count submissions using the dynamic relationship query
        return self.submissions.count()


    def get_leaderboard(self):
        """
        Get leaderboard for this contest

        Returns:
            list: List of users with their scores, sorted by score descending
        """
        # Import here to avoid circular imports between models
        from app.models.user import User
        from app.models.submission import Submission

        # Aggregate total scores per user for this contest
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

        # Format results as list of dictionaries
        return [
            {
                "user_id": row.id,
                "username": row.username,
                "total_score": row.total_score or 0,
            }
            for row in leaderboard_query
        ]


    # ------------------------------------------------------------------------
    # SCORING PARAMETERS (Multi-Parameter Scoring System)
    # ------------------------------------------------------------------------

    def set_scoring_parameters(self, params):
        """
        Set scoring parameters configuration

        Args:
            params: Dict or None
                {
                    "enabled": true,
                    "max_score": 100,
                    "min_score": 0,
                    "parameters": [
                        {"name": "Quality", "weight": 40, "description": "..."},
                        {"name": "Sources", "weight": 30, "description": "..."},
                        {"name": "Neutrality", "weight": 20, "description": "..."},
                        {"name": "Formatting", "weight": 10, "description": "..."}
                    ]
                }
        """
        if params is None:
            self.scoring_parameters = None
        elif isinstance(params, dict):
            # Validate that parameter weights sum to 100 (if enabled)
            if params.get("enabled") and "parameters" in params:
                total_weight = sum(p.get("weight", 0) for p in params["parameters"])
                if total_weight != 100:
                    raise ValueError(
                        f"Parameter weights must sum to 100, got {total_weight}"
                    )
            # Store as JSON string
            self.scoring_parameters = json.dumps(params)
        else:
            self.scoring_parameters = None


    def get_scoring_parameters(self):
        """
        Get scoring parameters configuration

        Returns:
            dict or None: Scoring parameters configuration
        """
        if not self.scoring_parameters:
            return None
        try:
            # Parse JSON string back to dictionary
            return json.loads(self.scoring_parameters)
        except json.JSONDecodeError:
            return None


    def is_multi_parameter_scoring_enabled(self):
        """
        Check if multi-parameter scoring is enabled for this contest

        Returns:
            bool: True if enabled, False otherwise
        """
        params = self.get_scoring_parameters()
        if not isinstance(params, dict):
            return False
        return params.get("enabled", False)


    def calculate_weighted_score(self, parameter_scores):
        """
        Calculate weighted score from individual parameter scores

        Args:
            parameter_scores: Dict mapping parameter names to scores (0-10)
                            Example: {"Quality": 8, "Sources": 7, ...}

        Returns:
            int: Final calculated score (clamped between min and max)
        """
        # Fall back to simple scoring if multi-parameter is disabled
        if not self.is_multi_parameter_scoring_enabled():
            return self.marks_setting_accepted

        # Extract scoring configuration
        scoring_config = self.get_scoring_parameters()
        max_score = scoring_config.get("max_score", 100)
        min_score = scoring_config.get("min_score", 0)
        parameters = scoring_config.get("parameters", [])

        # Calculate weighted average of parameter scores
        weighted_sum = 0.0
        for param in parameters:
            param_name = param["name"]
            weight = param["weight"] / 100.0  # Convert percentage to decimal
            score = parameter_scores.get(param_name, 0)  # Default to 0 if missing
            weighted_sum += score * weight

        # Scale weighted average (0-10) to final score range
        # Example: weighted_sum=8.5, max=100 → 8.5 * (100/10) = 85
        final_score = int(weighted_sum * (max_score / 10))

        # Clamp score between configured min and max bounds
        return max(min(final_score, max_score), min_score)


    # ------------------------------------------------------------------------
    # ORGANIZERS MANAGEMENT (Comma-Separated Storage)
    # ------------------------------------------------------------------------

    def set_organizers(self, organizers_list, creator_username=None):
        """
        Set organizers from list. Creator is always included.

        Args:
            organizers_list: List of organizer usernames
            creator_username: Username of creator (auto-added if provided)
        """
        if isinstance(organizers_list, list):
            # Remove duplicates and empty strings
            unique_organizers = list(set([
                username.strip()
                for username in organizers_list
                if username and username.strip()
            ]))

            # Ensure creator is always in the organizers list
            if creator_username:
                creator_username = creator_username.strip()
                if creator_username and creator_username not in unique_organizers:
                    # Add creator at the beginning
                    unique_organizers.insert(0, creator_username)
            elif self.created_by:
                # Fallback to created_by if no creator_username provided
                creator = self.created_by.strip()
                if creator and creator not in unique_organizers:
                    unique_organizers.insert(0, creator)

            # Convert list to comma-separated string
            self.organizers = ",".join(unique_organizers)
        else:
            # Fallback: set to creator only if invalid input
            if creator_username:
                self.organizers = creator_username.strip()
            elif self.created_by:
                self.organizers = self.created_by.strip()
            else:
                self.organizers = ""


    def get_organizers(self):
        """
        Get organizers as list of usernames.

        Returns:
            list: List of organizer usernames
        """
        if self.organizers:
            # Parse comma-separated string back to list
            return [
                username.strip()
                for username in self.organizers.split(",")
                if username.strip()
            ]
        return []


    def add_organizer(self, username):
        """
        Add a user as organizer for this contest.

        Args:
            username: Username to add as organizer

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        username = username.strip()
        if not username:
            return False, "Invalid username"

        # Check for duplicate
        current_organizers = self.get_organizers()
        if username in current_organizers:
            return False, f"{username} is already an organizer"

        # Add to list and persist
        current_organizers.append(username)
        self.set_organizers(current_organizers, self.created_by)

        return True, None


    def remove_organizer(self, username):
        """
        Remove a user as organizer from this contest.

        Args:
            username: Username to remove as organizer

        Returns:
            tuple: (success: bool, error_message: str or None)
        """
        username = username.strip()
        if not username:
            return False, "Invalid username"

        # Verify user is actually an organizer
        current_organizers = self.get_organizers()
        if username not in current_organizers:
            return False, f"{username} is not an organizer"

        # Prevent removing the contest creator
        if username == self.created_by:
            return False, "Cannot remove the contest creator from organizers"

        # Prevent removing the last organizer (contest must have at least one)
        if len(current_organizers) <= 1:
            return False, "Cannot remove the last organizer"

        # Remove from list and persist
        current_organizers.remove(username)
        self.set_organizers(current_organizers, self.created_by)

        return True, None


    def is_organizer(self, username):
        """
        Check if a user is an organizer for this contest.

        Args:
            username: Username to check

        Returns:
            bool: True if user is an organizer, False otherwise
        """
        if not username:
            return False

        username = username.strip()
        return username in self.get_organizers()


    # ------------------------------------------------------------------------
    # SERIALIZATION
    # ------------------------------------------------------------------------

    def to_dict(self):
        """
        Convert contest instance to dictionary for JSON serialization

        Returns:
            dict: Contest data
        """
        return {
            "id": self.id,
            "name": self.name,
            "project_name": self.project_name,
            "created_by": self.created_by,
            "description": self.description,

            # Convert dates to ISO format strings
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,

            # Parse JSON/comma-separated fields to native types
            "rules": self.get_rules(),
            "scoring_parameters": (
                self.get_scoring_parameters()
                if self.get_scoring_parameters()
                else {"enabled": False}  # Default for simple scoring
            ),

            # Scoring settings
            "marks_setting_accepted": self.marks_setting_accepted,
            "marks_setting_rejected": self.marks_setting_rejected,
            "allowed_submission_type": self.allowed_submission_type,

            # Article requirements
            "min_byte_count": self.min_byte_count,
            "min_reference_count": self.min_reference_count,
            "categories": self.get_categories(),

            # People management
            "jury_members": self.get_jury_members(),
            "organizers": self.get_organizers(),

            # Metadata - add 'Z' suffix to indicate UTC timezone
            # This ensures JavaScript interprets it as UTC, not local time
            "created_at": (
                (self.created_at.isoformat() + "Z") if self.created_at else None
            ),

            # Computed fields
            "submission_count": self.get_submission_count(),
            "status": self.get_status(),
        }


    def __repr__(self):
        """String representation of Contest instance"""
        return f"<Contest {self.name}>"