"""
Authentication and authorization middleware for the AI Ethics Testing Framework
"""

import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, session, g
from typing import Optional

from .database import EthicsDatabase
from .models import User, UserRole


class AuthManager:
    """Handles authentication and authorization"""
    
    def __init__(self, secret_key: str = None):
        self.secret_key = secret_key or os.getenv('SECRET_KEY', 'superskyhemmelig')
        self.db = EthicsDatabase()
    
    def generate_token(self, user: User) -> str:
        """Generate JWT token for user"""
        payload = {
            'user_id': user.id,
            'username': user.username,
            'role': user.role.value,
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify JWT token and return payload"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
    
    def get_current_user(self) -> Optional[User]:
        """Get current user from request"""
        # Try JWT token from Authorization header
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            payload = self.verify_token(token)
            if payload:
                return self.db.get_user_by_username(payload['username'])
        
        # Try session-based auth
        user_id = session.get('user_id')
        if user_id:
            # Get user from database by ID
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, username, email, password_hash, salt, role, 
                           is_active, created_at, last_login
                    FROM users WHERE id = %s AND is_active = TRUE
                """, (user_id,))
                
                row = cursor.fetchone()
                if row:
                    return User(
                        id=row[0],
                        username=row[1],
                        email=row[2],
                        password_hash=row[3],
                        salt=row[4],
                        role=UserRole(row[5]),
                        is_active=bool(row[6]),
                        created_at=row[7],
                        last_login=row[8]
                    )
        
        return None
    
    def login_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate user and return token"""
        user = self.db.authenticate_user(username, password)
        if user:
            token = self.generate_token(user)
            return {
                'token': token,
                'user': user.to_dict()
            }
        return None


# Initialize auth manager
auth_manager = AuthManager()


def login_required(f):
    """Decorator to require login for a route"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = auth_manager.get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """Decorator to require admin privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = auth_manager.get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        if not user.is_admin():
            return jsonify({'error': 'Admin privileges required'}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def superuser_required(f):
    """Decorator to require superuser privileges"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = auth_manager.get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        if not user.is_superuser():
            return jsonify({'error': 'Superuser privileges required'}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function


def can_edit_required(f):
    """Decorator to require edit privileges (researcher or higher)"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = auth_manager.get_current_user()
        if not user:
            return jsonify({'error': 'Authentication required'}), 401
        if not user.can_edit():
            return jsonify({'error': 'Edit privileges required'}), 403
        g.current_user = user
        return f(*args, **kwargs)
    return decorated_function
