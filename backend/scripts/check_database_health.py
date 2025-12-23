"""
Database Health Check Script
Checks for common database issues that might cause review submission failures
"""
import os
import sys

# Add the parent directory (backend) to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import app
from app.database import db
from app.models.submission import Submission
from app.models.user import User
from app.models.contest import Contest
from sqlalchemy import inspect

def check_database_health():
    """Check database schema and relationships"""
    with app.app_context():
        print("=" * 60)
        print("Database Health Check")
        print("=" * 60)
        
        # Check if tables exist
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\n[OK] Tables found: {', '.join(tables)}")
        
        # Check submissions table columns
        if 'submissions' in tables:
            columns = [col['name'] for col in inspector.get_columns('submissions')]
            required_columns = ['reviewed_by', 'reviewed_at', 'review_comment', 'user_id', 'status', 'score']
            print(f"\n[OK] Submissions table columns: {len(columns)} columns")
            missing = [col for col in required_columns if col not in columns]
            if missing:
                print(f"  [ERROR] Missing columns: {', '.join(missing)}")
            else:
                print(f"  [OK] All required columns present")
        
        # Check foreign keys
        if 'submissions' in tables:
            fks = inspector.get_foreign_keys('submissions')
            print(f"\n[OK] Foreign keys on submissions table: {len(fks)}")
            for fk in fks:
                print(f"  - {fk['name']}: {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
        
        # Check for sample data
        try:
            submission_count = Submission.query.count()
            user_count = User.query.count()
            contest_count = Contest.query.count()
            print(f"\n[OK] Data counts:")
            print(f"  - Submissions: {submission_count}")
            print(f"  - Users: {user_count}")
            print(f"  - Contests: {contest_count}")
            
            # Check for submissions with missing submitter
            if submission_count > 0:
                submissions_with_issues = []
                for sub in Submission.query.limit(10).all():
                    try:
                        # Try to access submitter
                        submitter = sub.submitter
                        if submitter is None:
                            submissions_with_issues.append(f"Submission {sub.id}: submitter is None")
                    except Exception as e:
                        submissions_with_issues.append(f"Submission {sub.id}: error accessing submitter - {str(e)}")
                
                if submissions_with_issues:
                    print(f"\n[ERROR] Issues found:")
                    for issue in submissions_with_issues:
                        print(f"  - {issue}")
                else:
                    print(f"\n[OK] Sample submissions have valid submitter relationships")
        except Exception as e:
            print(f"\n✗ Error checking data: {str(e)}")
        
        print("\n" + "=" * 60)
        print("Health check complete")
        print("=" * 60)

if __name__ == '__main__':
    check_database_health()
