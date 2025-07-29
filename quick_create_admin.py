#!/usr/bin/env python3
"""
Quick superuser creation script
"""

import sys
import os
sys.path.append('/home/skyforskning.no/forskning')

from src.models import User, UserRole
from src.database import EthicsDatabase

def create_admin_user():
    try:
        # Create superuser with fixed credentials
        db = EthicsDatabase()
        username = 'admin'
        email = 'admin@skyforskning.no'
        password = 'AIethics2025!'

        user = User(username=username, email=email, role=UserRole.SUPERUSER)
        user.set_password(password)

        # Save to database
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users (username, email, password_hash, salt, role)
                VALUES (%s, %s, %s, %s, %s)
            ''', (user.username, user.email, user.password_hash, user.salt, user.role.value))
            conn.commit()

        print('✅ Superuser opprettet!')
        print('')
        print('🔐 LOGIN INFORMASJON:')
        print('====================')
        print(f'Username: {username}')
        print(f'Email: {email}')
        print(f'Password: {password}')
        print(f'Role: superuser')
        print('')
        print('🌐 Login på: https://skyforskning.no/login')
        
    except Exception as e:
        print(f'❌ Feil ved opprettelse av bruker: {e}')

if __name__ == '__main__':
    create_admin_user()
