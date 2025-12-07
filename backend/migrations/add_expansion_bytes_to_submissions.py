#!/usr/bin/env python3
"""
Migration script: Add article_expansion_bytes column to submissions table

This script adds the following column to the submissions table:
- article_expansion_bytes: Bytes added between contest start and submission time

Usage:
    python migrations/add_expansion_bytes_to_submissions.py
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
    Run the migration to add article_expansion_bytes column
    """
    print("=" * 60)
    print("Migration: Add Article Expansion Bytes to Submissions Table")
    print("=" * 60)
    
    with app.app_context():
        try:
            # Check if column already exists by trying to query it
            # If it doesn't exist, we'll get an error and can add it
            try:
                db.session.execute(text("SELECT article_expansion_bytes FROM submissions LIMIT 1"))
                print("[INFO] Column 'article_expansion_bytes' already exists")
                print("[SKIP] Migration not needed.")
                return True
            except Exception:
                # Column doesn't exist, proceed with migration
                pass
            
            print("[STEP 1] Adding article_expansion_bytes column...")
            try:
                db.session.execute(text("""
                    ALTER TABLE submissions 
                    ADD COLUMN article_expansion_bytes INT NULL
                """))
                print("  [OK] article_expansion_bytes column added")
                
                # Commit changes
                db.session.commit()
                print("\n[SUCCESS] Migration completed successfully!")
                print("The article_expansion_bytes column has been added to the submissions table.")
                return True
                
            except Exception as e:
                print(f"  [WARNING] Error adding article_expansion_bytes: {e}")
                db.session.rollback()
                return False
            
        except Exception as e:
            print(f"\n[ERROR] Migration failed: {e}")
            db.session.rollback()
            return False

if __name__ == '__main__':
    success = run_migration()
    sys.exit(0 if success else 1)
