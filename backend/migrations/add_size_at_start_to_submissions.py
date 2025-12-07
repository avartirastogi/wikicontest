#!/usr/bin/env python3
"""
Migration script: Add article_size_at_start column to submissions table

This script adds the following column to the submissions table:
- article_size_at_start: Article size in bytes at contest start date

Usage:
    python migrations/add_size_at_start_to_submissions.py
"""

import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import app, db
from sqlalchemy import text

def run_migration():
    """
    Run the migration to add article_size_at_start column
    """
    print("=" * 60)
    print("Migration: Add Article Size at Start to Submissions Table")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check if column already exists by trying to query it
            # If it doesn't exist, we'll get an error and can add it
            try:
                db.session.execute(text("SELECT article_size_at_start FROM submissions LIMIT 1"))
                print("[INFO] Column 'article_size_at_start' already exists")
                print("[SKIP] Migration not needed.")
                return True
            except Exception:
                # Column doesn't exist, proceed with migration
                pass
            
            print("[STEP 1] Adding article_size_at_start column...")
            try:
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    ADD COLUMN article_size_at_start INT NULL
                """))
                print("  [OK] article_size_at_start column added")
                
                # Commit changes
                db.session.commit()
                print("\n[SUCCESS] Migration completed successfully!")
                print("The article_size_at_start column has been added to the submissions table.")
                return True
                
            except Exception as e:
                print(f"  [WARNING] Error adding article_size_at_start: {e}")
                db.session.rollback()
                return False
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
