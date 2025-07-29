#!/usr/bin/env python3
"""
Create a superuser for the AI Ethics Testing Framework
"""

import os
import sys
import getpass
from pathlib import Path
from dotenv import load_dotenv

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Load environment variables
load_dotenv()

from src.database import EthicsDatabase
from src.models import UserRole


def create_superuser():
    """Interactive superuser creation"""
    print("🔐 AI Ethics Framework - Create Superuser")
    print("=" * 50)
    
    try:
        # Initialize database
        db = EthicsDatabase()
        
        # Check if any superusers exist
        existing_superusers = db.get_superusers()
        if existing_superusers:
            print(f"⚠️  Warning: {len(existing_superusers)} superuser(s) already exist:")
            for user in existing_superusers:
                print(f"   - {user.username} ({user.email})")
            
            confirm = input("\nDo you want to create another superuser? (y/N): ").strip().lower()
            if confirm != 'y':
                print("Operation cancelled.")
                return
        
        # Get user input
        print("\nEnter superuser details:")
        username = input("Username: ").strip()
        
        if not username:
            print("❌ Username cannot be empty")
            return
        
        email = input("Email: ").strip()
        
        if not email:
            print("❌ Email cannot be empty")
            return
        
        # Get password securely
        while True:
            password = getpass.getpass("Password: ")
            if len(password) < 8:
                print("❌ Password must be at least 8 characters long")
                continue
            
            confirm_password = getpass.getpass("Confirm password: ")
            if password != confirm_password:
                print("❌ Passwords do not match")
                continue
            
            break
        
        # Create superuser
        try:
            user = db.create_user(
                username=username,
                email=email,
                password=password,
                role=UserRole.SUPERUSER
            )
            
            print("\n✅ Superuser created successfully!")
            print(f"   Username: {user.username}")
            print(f"   Email: {user.email}")
            print(f"   Role: {user.role.value}")
            print(f"   Created: {user.created_at}")
            
        except ValueError as e:
            print(f"❌ Error creating user: {e}")
            return
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        print("\nMake sure MariaDB is running and accessible with the configured credentials:")
        print(f"   Host: {os.getenv('DB_HOST', 'localhost')}")
        print(f"   Port: {os.getenv('DB_PORT', '3306')}")
        print(f"   Database: {os.getenv('DB_NAME', 'skyforskning')}")
        print(f"   User: {os.getenv('DB_USER', 'skyforskning')}")
        return


def list_users():
    """List all users"""
    try:
        db = EthicsDatabase()
        users = db.list_users()
        
        if not users:
            print("No users found.")
            return
        
        print(f"\n👥 All Users ({len(users)} total):")
        print("-" * 80)
        print(f"{'ID':<5} {'Username':<20} {'Email':<30} {'Role':<12} {'Active':<8} {'Created'}")
        print("-" * 80)
        
        for user in users:
            created = user.created_at.strftime("%Y-%m-%d") if user.created_at else "Unknown"
            active = "Yes" if user.is_active else "No"
            print(f"{user.id:<5} {user.username:<20} {user.email:<30} {user.role.value:<12} {active:<8} {created}")
        
    except Exception as e:
        print(f"❌ Error listing users: {e}")


def main():
    """Main function"""
    if len(sys.argv) > 1 and sys.argv[1] == "--list":
        list_users()
    else:
        create_superuser()


if __name__ == "__main__":
    main()
