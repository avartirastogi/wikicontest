#!/usr/bin/env python3
"""
Fix Alembic version table when migration files are missing.

This script updates the alembic_version table to match the actual
migration files in the repository.

Usage:
    python scripts/fix_alembic_version.py <target_revision>
    
Example:
    python scripts/fix_alembic_version.py fc55a0c85ffc
"""

import sys
import os

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import create_app
from app.database import db

def main():
    """
    Update alembic_version table to the specified revision.
    """
    if len(sys.argv) < 2:
        print("Usage: python scripts/fix_alembic_version.py <target_revision>")
        print("\nExample:")
        print("  python scripts/fix_alembic_version.py fc55a0c85ffc")
        sys.exit(1)
    
    target_revision = sys.argv[1]
    
    # Create Flask app to get database connection
    app = create_app()
    
    with app.app_context():
        try:
            # Update alembic_version table directly
            # This bypasses Alembic's normal checks
            db.session.execute(
                db.text("UPDATE alembic_version SET version_num = :revision"),
                {"revision": target_revision}
            )
            db.session.commit()
            
            print(f"Successfully updated alembic_version to: {target_revision}")
            print("\nYou can now run:")
            print("  python -m alembic current")
            print("  python -m alembic revision --autogenerate -m 'Your message'")
            
        except Exception as e:
            print(f"Error updating alembic_version: {e}")
            print("\nTroubleshooting:")
            print("1. Make sure your database is running")
            print("2. Check your DATABASE_URL in .env file")
            print("3. Verify the alembic_version table exists")
            sys.exit(1)

if __name__ == '__main__':
    main()

