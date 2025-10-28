"""
Submission Model for WikiContest Application
Defines the Submission table and related functionality
"""

from database import db
from datetime import datetime

class Submission(db.Model):
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
    
    __tablename__ = 'submissions'
    
    # Primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Foreign keys
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    contest_id = db.Column(db.Integer, db.ForeignKey('contests.id'), nullable=False)
    
    # Submission content
    article_title = db.Column(db.String(500), nullable=False)
    article_link = db.Column(db.String(1000), nullable=False)
    
    # Submission status and scoring
    status = db.Column(db.String(20), nullable=False, default='pending')
    score = db.Column(db.Integer, default=0, nullable=False)
    
    # Timestamp
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'contest_id', name='unique_user_contest_submission'),
    )
    
    def __init__(self, user_id, contest_id, article_title, article_link, status='pending'):
        """
        Initialize a new Submission instance
        
        Args:
            user_id: ID of the user making the submission
            contest_id: ID of the contest being submitted to
            article_title: Title of the submitted article
            article_link: URL to the submitted article
            status: Initial status (defaults to 'pending')
        """
        self.user_id = user_id
        self.contest_id = contest_id
        self.article_title = article_title
        self.article_link = article_link
        self.status = status
        self.score = 0
    
    def is_pending(self):
        """
        Check if submission is pending
        
        Returns:
            bool: True if submission is pending, False otherwise
        """
        return self.status == 'pending'
    
    def is_accepted(self):
        """
        Check if submission is accepted
        
        Returns:
            bool: True if submission is accepted, False otherwise
        """
        return self.status == 'accepted'
    
    def is_rejected(self):
        """
        Check if submission is rejected
        
        Returns:
            bool: True if submission is rejected, False otherwise
        """
        return self.status == 'rejected'
    
    def update_status(self, new_status, contest=None):
        """
        Update submission status and score
        
        Args:
            new_status: New status ('accepted' or 'rejected')
            contest: Contest instance (optional, will be fetched if not provided)
            
        Returns:
            bool: True if status was updated, False if no change needed
        """
        # Check if status is already set
        if self.status == new_status:
            return False
        
        # Get contest if not provided
        if not contest:
            contest = self.contest
        
        # Calculate new score based on contest settings
        if new_status == 'accepted':
            new_score = contest.marks_setting_accepted
        elif new_status == 'rejected':
            new_score = contest.marks_setting_rejected
        else:
            new_score = 0
        
        # Calculate score difference for user
        score_difference = new_score - self.score
        
        # Update submission
        old_score = self.score
        self.status = new_status
        self.score = new_score
        
        # Update user's total score
        if score_difference != 0:
            self.submitter.update_score(score_difference)
        
        # Commit changes
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
            'id': self.id,
            'user_id': self.user_id,
            'contest_id': self.contest_id,
            'article_title': self.article_title,
            'article_link': self.article_link,
            'status': self.status,
            'score': self.score,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }
        
        if include_user_info:
            data.update({
                'username': self.submitter.username,
                'email': self.submitter.email,
                'contest_name': self.contest.name
            })
        
        return data
    
    def save(self):
        """
        Save submission to database
        """
        db.session.add(self)
        db.session.commit()
    
    def delete(self):
        """
        Delete submission from database
        """
        db.session.delete(self)
        db.session.commit()
    
    def __repr__(self):
        """String representation of Submission instance"""
        return f'<Submission {self.id}: {self.article_title}>'