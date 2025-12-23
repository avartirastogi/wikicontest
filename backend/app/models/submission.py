"""
Submission Model for WikiContest Application
Defines the Submission table and related functionality
"""

from datetime import datetime, timezone
from app.database import db
from app.models.base_model import BaseModel


class Submission(BaseModel):
    """
    Submission model representing user submissions to contests

    Attributes:
        id: Primary key, auto-incrementing integer
        user_id: Foreign key to users table
        contest_id: Foreign key to contests table
        article_title: Title of the submitted article
        article_link: URL link to the submitted article
        status: Status of the submission (pending, accepted, rejected)
        score: Score awarded to the submission
        submitted_at: Timestamp when submission was made
    """

    __tablename__ = "submissions"

    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    contest_id = db.Column(db.Integer, db.ForeignKey("contests.id"), nullable=False)

    # Submission content
    article_title = db.Column(db.String(500), nullable=False)
    article_link = db.Column(db.String(1000), nullable=False)

    # Article metadata (fetched from MediaWiki API)
    # Author from latest revision at submission time (most recent editor)
    article_author = db.Column(db.String(200), nullable=True)
    article_created_at = db.Column(
        db.DateTime, nullable=True
    )  # When article was created (ISO format string)
    article_word_count = db.Column(
        db.Integer, nullable=True
    )  # Word count/size of article (in bytes)
    article_page_id = db.Column(db.String(50), nullable=True)  # MediaWiki page ID
    article_size_at_start = db.Column(
        db.Integer, nullable=True
    )  # Article size in bytes at contest start
    # Bytes added between contest start and submission time
    article_expansion_bytes = db.Column(db.Integer, nullable=True)

    # Submission status and scoring
    # pending | accepted | rejected | auto_rejected
    status = db.Column(db.String(20), nullable=False, default="pending")
    score = db.Column(db.Integer, default=0, nullable=False)

    # Review metadata (jury / organizer review)
    reviewed_by = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    review_comment = db.Column(db.Text, nullable=True)

    # Timestamp
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    submitter = db.relationship(
        "User", foreign_keys=[user_id], back_populates="submissions"
    )

    reviewer = db.relationship(
        "User",
        foreign_keys=[reviewed_by],
        primaryjoin="Submission.reviewed_by == User.id",
        back_populates="reviewed_submissions",
        overlaps="submissions",
    )

    contest = db.relationship("Contest", back_populates="submissions")

    # Constraints
    __table_args__ = (
        db.UniqueConstraint(
            "user_id", "contest_id", name="unique_user_contest_submission"
        ),
    )

    def __init__(
        self,
        user_id,
        contest_id,
        article_title,
        article_link,
        status="pending",
        article_author=None,
        article_created_at=None,
        article_word_count=None,
        article_page_id=None,
        article_size_at_start=None,
        article_expansion_bytes=None,
    ):
        """
        Initialize a new Submission instance

        Args:
            user_id: ID of the user making the submission
            contest_id: ID of the contest being submitted to
            article_title: Title of the submitted article
            article_link: URL to the submitted article
            status: Initial status (defaults to 'pending')
            article_author: Author from latest revision at submission time (optional, fetched from MediaWiki API)
            article_created_at: When article was created (optional, fetched from MediaWiki API)
            article_word_count: Word count/size of article in bytes (optional, fetched from MediaWiki API)
            article_page_id: MediaWiki page ID (optional, fetched from MediaWiki API)
            article_size_at_start: Article size in bytes at contest start (optional)
            article_expansion_bytes: Bytes added between contest start and submission time (optional)
        """
        self.user_id = user_id
        self.contest_id = contest_id
        self.article_title = article_title
        self.article_link = article_link
        self.status = status
        self.score = 0
        self.article_author = article_author
        self.article_created_at = article_created_at
        self.article_word_count = article_word_count
        self.article_page_id = article_page_id
        self.article_size_at_start = article_size_at_start
        self.article_expansion_bytes = article_expansion_bytes
        self.reviewed_by = None
        self.reviewed_at = None
        self.review_comment = None

    def is_pending(self):
        """
        Check if submission is pending

        Returns:
            bool: True if submission is pending, False otherwise
        """
        return self.status == "pending"

    def is_accepted(self):
        """
        Check if submission is accepted

        Returns:
            bool: True if submission is accepted, False otherwise
        """
        return self.status == "accepted"

    def is_rejected(self):
        """
        Check if submission is rejected

        Returns:
            bool: True if submission is rejected, False otherwise
        """
        return self.status == "rejected"

    def update_status(
        self, new_status, reviewer=None, score=None, comment=None, contest=None
    ):
        """
        Update submission status with review metadata

        Args:
            new_status: accepted | rejected | auto_rejected
            reviewer: User instance who reviewed
            score: Optional score override
            comment: Optional review comment
            contest: Contest instance
        """
        if self.status == new_status:
            return False

        if not contest:
            contest = self.contest

        # Determine final score
        if new_status == "accepted":
            final_score = score if score is not None else contest.marks_setting_accepted
        elif new_status == "rejected":
            final_score = contest.marks_setting_rejected
        else:  # auto_rejected
            final_score = 0

        score_difference = final_score - self.score

        # Update submission
        self.status = new_status
        self.score = final_score
        self.reviewed_by = reviewer.id if reviewer else None
        self.reviewed_at = datetime.now(timezone.utc)
        self.review_comment = comment

        # Update user's total score
        if score_difference != 0:
            # Ensure submitter is loaded - if not, load it explicitly
            if self.submitter is None:
                from app.models.user import User
                self.submitter = User.query.get(self.user_id)
                if self.submitter is None:
                    raise ValueError(f"Submitter user with id {self.user_id} not found")
            self.submitter.update_score(score_difference)

        db.session.commit()
        return True

    def can_be_judged_by(self, user):
        """
        Check if a user can judge this submission

        Args:
            user: User instance to check

        Returns:
            bool: True if user can judge submission, False otherwise
        """
        # Admin can judge all submissions
        if user.is_admin():
            return True

        # Jury members can judge submissions in their contests
        if user.is_jury_member(self.contest):
            return True

        return False

    def can_be_viewed_by(self, user):
        """
        Check if a user can view this submission

        Args:
            user: User instance to check

        Returns:
            bool: True if user can view submission, False otherwise
        """
        # Admin can view all submissions
        if user.is_admin():
            return True

        # User can view their own submissions
        if self.user_id == user.id:
            return True

        # Jury members can view submissions in their contests
        if user.is_jury_member(self.contest):
            return True

        # Contest creators can view submissions in their contests
        if user.is_contest_creator(self.contest):
            return True

        return False

    def to_dict(self, include_user_info=False):
        """
        Convert submission instance to dictionary for JSON serialization

        Args:
            include_user_info: Whether to include user information

        Returns:
            dict: Submission data
        """
        data = {
            "id": self.id,
            "user_id": self.user_id,
            "contest_id": self.contest_id,
            "article_title": self.article_title,
            "article_link": self.article_link,
            "status": self.status,
            "score": self.score,
            # Format datetime as ISO string with 'Z' suffix to indicate UTC
            # This ensures JavaScript interprets it as UTC, not local time
            "submitted_at": (
                (self.submitted_at.isoformat() + "Z") if self.submitted_at else None
            ),
            # Article metadata for judges and organizers
            "article_author": self.article_author,
            "article_created_at": self.article_created_at,
            "article_word_count": self.article_word_count,
            "article_page_id": self.article_page_id,
            "article_size_at_start": self.article_size_at_start,
            "article_expansion_bytes": self.article_expansion_bytes,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": (
                self.reviewed_at.isoformat() + "Z" if self.reviewed_at else None
            ),
            "review_comment": self.review_comment,
            "already_reviewed": self.reviewed_at is not None,
        }

        if include_user_info:
            data.update(
                {
                    "username": self.submitter.username,
                    "email": self.submitter.email,
                    "contest_name": self.contest.name,
                }
            )

        return data

    def __repr__(self):
        """String representation of Submission instance"""
        return f"<Submission {self.id}: {self.article_title}>"
