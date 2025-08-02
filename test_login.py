#!/usr/bin/env python3
"""
Test login for superadmin user Terje
"""

import pymysql as MySQLdb
import hashlib

def test_login(username, password):
    """Test login with the given credentials"""
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'skyforskning',
        'passwd': 'Klokken!12!?!',
        'db': 'skyforskning',
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    try:
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()
        
        # Get user from database
        cursor.execute("""
            SELECT username, password_hash, salt, role, email 
            FROM users 
            WHERE username = %s AND is_active = 1
        """, (username,))
        
        user_data = cursor.fetchone()
        
        if user_data:
            stored_username, stored_hash, salt, role, email = user_data
            print(f"Found user: {stored_username}")
            print(f"Role: {role}")
            print(f"Email: {email}")
            print(f"Salt length: {len(salt) if salt else 'No salt'}")
            print(f"Stored hash length: {len(stored_hash) if stored_hash else 'No hash'}")
            
            # Test password
            if salt:
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                if password_hash == stored_hash:
                    print("✅ Password verification SUCCESSFUL")
                    return True
                else:
                    print("❌ Password verification FAILED")
                    print(f"Expected: {stored_hash}")
                    print(f"Computed: {password_hash}")
                    return False
            else:
                print("❌ No salt found - password system not properly initialized")
                return False
        else:
            print(f"❌ User '{username}' not found or inactive")
            return False
    
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("Testing login for superadmin user...")
    success = test_login("Terje", "KlokkenTerje2025")
    exit(0 if success else 1)
