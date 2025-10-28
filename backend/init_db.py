#!/usr/bin/env python3
"""
Database initialization script for WikiContest Flask Application
"""

import os
import sys
from datetime import datetime, date, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models.user import User
from models.contest import Contest
from models.submission import Submission

def create_tables():
    """
    Create all database tables
    """
    print("Creating database tables...")
    
    with app.app_context():
        try:
            db.create_all()
            print("✅ Database tables created successfully!")
        except Exception as e:
            print(f"❌ Error creating tables: {e}")
            return False
    
    return True

# Note: Sample/demo data seeding has been removed to keep this script
# production-friendly. Developers can add their own seed scripts separately
# if needed.

def reset_database():
    """
    Drop all tables and recreate them
    """
    print("Resetting database...")
    
    with app.app_context():
        try:
            db.drop_all()
            print("✅ Dropped all tables")
            db.create_all()
            print("✅ Recreated all tables")
        except Exception as e:
            print(f"❌ Error resetting database: {e}")
            return False
    
    return True

def main():
    """
    Main function to initialize database
    """
    print("WikiContest Database Initialization")
    print("=" * 40)
    
    # Check command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == 'reset':
            if reset_database():
                print("✅ Database reset completed!")
            else:
                print("❌ Database reset failed!")
                sys.exit(1)
        elif command == 'seed':
            if create_tables() and seed_sample_data():
                print("✅ Database initialization with sample data completed!")
            else:
                print("❌ Database initialization failed!")
                sys.exit(1)
        else:
            print(f"Unknown command: {command}")
            print("Available commands: reset")
            sys.exit(1)
    else:
        # Default: just create tables
        if create_tables():
            print("✅ Database initialization completed!")
        else:
            print("❌ Database initialization failed!")
            sys.exit(1)

if __name__ == '__main__':
    main()