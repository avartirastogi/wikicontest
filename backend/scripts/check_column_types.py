"""
Check the actual column types in the database
"""
import os
import sys

# Add the parent directory (backend) to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import app
from app.database import db
from sqlalchemy import inspect, text

def check_column_types():
    """Check column types in submissions table"""
    with app.app_context():
        print("=" * 60)
        print("Checking column types")
        print("=" * 60)
        
        inspector = inspect(db.engine)
        
        # Check submissions table
        columns = inspector.get_columns('submissions')
        print("\nSubmissions table columns:")
        for col in columns:
            if col['name'] in ['reviewed_by', 'user_id', 'reviewed_at', 'review_comment']:
                print(f"  {col['name']}: {col['type']} (nullable={col['nullable']})")
        
        # Check users table
        columns = inspector.get_columns('users')
        print("\nUsers table columns:")
        for col in columns:
            if col['name'] in ['id', 'username']:
                print(f"  {col['name']}: {col['type']} (nullable={col['nullable']})")
        
        # Check foreign keys
        print("\nForeign keys on submissions:")
        fks = inspector.get_foreign_keys('submissions')
        for fk in fks:
            if 'reviewed_by' in fk['constrained_columns']:
                print(f"  Name: {fk['name']}")
                print(f"  Columns: {fk['constrained_columns']}")
                print(f"  Referenced table: {fk['referred_table']}")
                print(f"  Referenced columns: {fk['referred_columns']}")
        
        # Try to get the actual SQL type
        print("\nChecking actual SQL types:")
        result = db.session.execute(text(
            "SHOW COLUMNS FROM submissions WHERE Field IN ('reviewed_by', 'user_id')"
        ))
        for row in result:
            print(f"  {row[0]}: {row[1]}")

if __name__ == '__main__':
    check_column_types()
