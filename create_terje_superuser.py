#!/usr/bin/env python3
"""
Create Terje superuser for the AI Ethics Testing Framework
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
load_dotenv()

from src.database import EthicsDatabase
from src.models import UserRole


def create_terje_superuser():
    """Create Terje superuser with specified credentials"""
    print("🔐 Creating Terje superuser...")
    
    try:
        # Initialize database
        db = EthicsDatabase()
        
        # User details
        username = "Terje"
        email = "terje@skyforskning.no"
        password = "KlokkenTerje2025"
        
        # Check if user already exists
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT username, email, role FROM users WHERE username = %s OR email = %s", 
                         (username, email))
            existing = cursor.fetchone()
            
            if existing:
                print(f"⚠️  User already exists: {existing[0]} ({existing[1]}) - {existing[2]}")
                print("Updating password and role to superuser...")
                
                # Update existing user
                from src.models import User
                password_hash, salt = User.hash_password(password)
                cursor.execute("""
                    UPDATE users 
                    SET password_hash = %s, salt = %s, role = %s, is_active = TRUE
                    WHERE username = %s
                """, (password_hash, salt, UserRole.SUPERUSER.value, username))
                conn.commit()
                
                print(f"✅ Updated user '{username}' to superuser with new password")
            else:
                # Create new user
                user = db.create_user(
                    username=username,
                    email=email,
                    password=password,
                    role=UserRole.SUPERUSER
                )
                print(f"✅ Created superuser: {user.username} ({user.email})")
            
            # Verify creation/update
            cursor.execute("SELECT username, email, role, is_active FROM users WHERE username = %s", (username,))
            result = cursor.fetchone()
            if result:
                print(f"✅ Verified: {result[0]} ({result[1]}) - {result[2]} - Active: {result[3]}")
                print(f"🔑 Login credentials:")
                print(f"   Username: {username}")
                print(f"   Password: {password}")
            else:
                print("❌ Failed to verify user creation")
                
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    create_terje_superuser()
