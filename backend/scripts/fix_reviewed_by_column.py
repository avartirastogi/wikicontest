"""
Fix the reviewed_by column type and foreign key
The column is currently VARCHAR(50) but should be INTEGER
"""
import os
import sys

# Add the parent directory (backend) to Python path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from app import app
from app.database import db
from sqlalchemy import text

def fix_reviewed_by_column():
    """Fix the reviewed_by column type and foreign key"""
    with app.app_context():
        print("=" * 60)
        print("Fixing reviewed_by column type and foreign key")
        print("=" * 60)
        
        try:
            # Step 1: Drop the incorrect foreign key if it exists
            print("\n[1] Dropping incorrect foreign key constraint...")
            try:
                db.session.execute(text(
                    "ALTER TABLE submissions DROP FOREIGN KEY fk_submissions_reviewed_by_users"
                ))
                db.session.commit()
                print("[OK] Dropped incorrect constraint")
            except Exception as e:
                db.session.rollback()
                print(f"[INFO] Constraint may not exist: {str(e)}")
            
            # Step 2: Check if there are any non-null values that need conversion
            print("\n[2] Checking for existing data...")
            result = db.session.execute(text(
                "SELECT COUNT(*) as count FROM submissions WHERE reviewed_by IS NOT NULL"
            ))
            count = result.fetchone()[0]
            print(f"[INFO] Found {count} submissions with reviewed_by set")
            
            if count > 0:
                print("[WARNING] There are existing reviewed_by values.")
                print("These need to be converted from username to user ID.")
                print("Please review the data and convert manually if needed.")
                response = input("Continue anyway? (yes/no): ")
                if response.lower() != 'yes':
                    print("Aborted.")
                    return
            
            # Step 3: Clear any existing values (they're wrong type anyway)
            print("\n[3] Clearing existing reviewed_by values...")
            db.session.execute(text(
                "UPDATE submissions SET reviewed_by = NULL WHERE reviewed_by IS NOT NULL"
            ))
            db.session.commit()
            print("[OK] Cleared existing values")
            
            # Step 4: Alter the column type from VARCHAR to INTEGER
            print("\n[4] Altering column type from VARCHAR(50) to INTEGER...")
            db.session.execute(text(
                "ALTER TABLE submissions MODIFY COLUMN reviewed_by INTEGER NULL"
            ))
            db.session.commit()
            print("[OK] Column type changed to INTEGER")
            
            # Step 5: Create the correct foreign key constraint
            print("\n[5] Creating correct foreign key constraint...")
            db.session.execute(text(
                "ALTER TABLE submissions "
                "ADD CONSTRAINT fk_submissions_reviewed_by_users "
                "FOREIGN KEY (reviewed_by) REFERENCES users(id)"
            ))
            db.session.commit()
            print("[OK] Created correct constraint")
            
            print("\n" + "=" * 60)
            print("Column and foreign key fixed successfully!")
            print("=" * 60)
            print("\nNote: Any existing reviewed_by values have been cleared.")
            print("You may need to re-review submissions if there were any.")
            
        except Exception as e:
            db.session.rollback()
            print(f"\n[ERROR] Failed to fix column: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == '__main__':
    fix_reviewed_by_column()
