"""
Fix the reviewed_by foreign key constraint
The constraint incorrectly references users.username instead of users.id
"""
import os
import sys

# Add the parent directory (backend) to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import app
from app.database import db
from sqlalchemy import text

def fix_foreign_key():
    """Fix the reviewed_by foreign key constraint"""
    with app.app_context():
        print("=" * 60)
        print("Fixing reviewed_by foreign key constraint")
        print("=" * 60)
        
        try:
            # Drop the incorrect foreign key constraint
            print("\n[1] Dropping incorrect foreign key constraint...")
            db.session.execute(text(
                "ALTER TABLE submissions DROP FOREIGN KEY fk_submissions_reviewed_by_users"
            ))
            db.session.commit()
            print("[OK] Dropped incorrect constraint")
            
            # Create the correct foreign key constraint
            print("\n[2] Creating correct foreign key constraint...")
            db.session.execute(text(
                "ALTER TABLE submissions "
                "ADD CONSTRAINT fk_submissions_reviewed_by_users "
                "FOREIGN KEY (reviewed_by) REFERENCES users(id)"
            ))
            db.session.commit()
            print("[OK] Created correct constraint")
            
            print("\n" + "=" * 60)
            print("Foreign key constraint fixed successfully!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Failed to fix constraint: {str(e)}")
            print("\nYou may need to run this manually in your database:")
            print("  ALTER TABLE submissions DROP FOREIGN KEY fk_submissions_reviewed_by_users;")
            print("  ALTER TABLE submissions ADD CONSTRAINT fk_submissions_reviewed_by_users")
            print("    FOREIGN KEY (reviewed_by) REFERENCES users(id);")
            sys.exit(1)

if __name__ == '__main__':
    fix_foreign_key()
