"""
Data storage and retrieval for the AI Ethics Testing Framework
"""

import json
import pymysql as MySQLdb
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from .models import (
    EthicalDilemma, ModelResponse, StanceChange,
    TestSession, EthicalStance, DilemmaCategory, User, UserRole
)


class EthicsDatabase:
    """MariaDB database for storing ethics test data"""
    
    def __init__(self):
        """Initialize database connection parameters from environment"""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),  # Changed from 'mariadb' to 'localhost'
            'port': int(os.getenv('DB_PORT', '3306')),
            'user': os.getenv('DB_USER', 'skyforskning'),
            'passwd': os.getenv('DB_PASSWORD', 'Klokken!12!?!'),
            'db': os.getenv('DB_NAME', 'skyforskning'),
            'charset': 'utf8mb4',
            'autocommit': True
        }
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Responses table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    prompt_id VARCHAR(255) NOT NULL,
                    model VARCHAR(255) NOT NULL,
                    timestamp DATETIME NOT NULL,
                    response_text TEXT NOT NULL,
                    sentiment_score DECIMAL(5,4) NOT NULL,
                    stance VARCHAR(100) NOT NULL,
                    certainty_score DECIMAL(5,4) NOT NULL,
                    keywords TEXT NOT NULL,
                    response_length INT NOT NULL,
                    session_id VARCHAR(255),
                    INDEX idx_responses_prompt_id (prompt_id),
                    INDEX idx_responses_model (model),
                    INDEX idx_responses_timestamp (timestamp)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Stance changes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stance_changes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    prompt_id VARCHAR(255) NOT NULL,
                    model VARCHAR(255) NOT NULL,
                    initial_stance VARCHAR(100) NOT NULL,
                    final_stance VARCHAR(100) NOT NULL,
                    change_magnitude DECIMAL(5,4) NOT NULL,
                    change_direction VARCHAR(50) NOT NULL,
                    timestamp DATETIME NOT NULL,
                    session_id VARCHAR(255),
                    INDEX idx_stance_changes_prompt_id (prompt_id),
                    INDEX idx_stance_changes_model (model)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Test sessions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    session_id VARCHAR(255) PRIMARY KEY,
                    timestamp DATETIME NOT NULL,
                    model VARCHAR(255) NOT NULL,
                    completion_rate DECIMAL(5,4) NOT NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    password_hash VARCHAR(256) NOT NULL,
                    salt VARCHAR(64) NOT NULL,
                    role ENUM('viewer', 'researcher', 'admin', 'superuser') DEFAULT 'viewer',
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    last_login DATETIME NULL,
                    INDEX idx_users_username (username),
                    INDEX idx_users_email (email)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # API keys table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    provider VARCHAR(50) NOT NULL,
                    name VARCHAR(100) NOT NULL,
                    key_value TEXT NOT NULL,
                    status ENUM('active', 'inactive', 'error') DEFAULT 'inactive',
                    last_tested TIMESTAMP NULL,
                    response_time INT DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY unique_provider_name (provider, name)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # System settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS system_settings (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setting_key VARCHAR(100) NOT NULL UNIQUE,
                    setting_value TEXT NOT NULL,
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            
            # Insert default settings
            cursor.execute("""
                INSERT IGNORE INTO system_settings (setting_key, setting_value, description) VALUES
                ('testing_frequency', '30', 'How often to run LLM tests (in days)'),
                ('last_test_run', '0', 'Unix timestamp of last test run'),
                ('enable_change_detection', '1', 'Enable detection of changes in LLM responses')
            """)
    
    @contextmanager
    def get_connection(self):
        """Get a MariaDB database connection with automatic cleanup"""
        conn = None
        try:
            conn = MySQLdb.connect(**self.db_config)
            yield conn
        except MySQLdb.Error as e:
            if conn:
                conn.rollback()
            raise Exception(f"Database error: {e}")
        finally:
            if conn:
                conn.close()
    
    def save_response(self, response: ModelResponse, 
                     session_id: Optional[str] = None):
        """Save a model response to the database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO responses
                (prompt_id, model, timestamp, response_text, sentiment_score,
                 stance, certainty_score, keywords, response_length, session_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                response.prompt_id,
                response.model,
                response.timestamp,
                response.response_text,
                response.sentiment_score,
                response.stance.value,
                response.certainty_score,
                json.dumps(response.keywords),
                response.response_length,
                session_id
            ))
    
    def save_stance_change(self, change: StanceChange):
        """Save a detected stance change"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO stance_changes
                (prompt_id, model, initial_stance, final_stance, 
                 change_magnitude, change_direction, timestamp, session_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                change.prompt_id,
                change.model,
                change.initial_stance.value,
                change.final_stance.value,
                change.change_magnitude,
                change.change_direction,
                change.timestamp,
                getattr(change, 'session_id', None)
            ))
    
    def save_test_session(self, session: TestSession):
        """Save a complete test session"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Save session metadata
            cursor.execute("""
                INSERT INTO test_sessions
                (session_id, timestamp, model, completion_rate)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                timestamp = VALUES(timestamp),
                model = VALUES(model),
                completion_rate = VALUES(completion_rate)
            """, (
                session.session_id,
                session.timestamp,
                session.model,
                session.completion_rate
            ))
            
            # Save all responses with session_id
            for response in session.responses:
                self.save_response(response, session.session_id)
    
    def get_responses_for_prompt(self, prompt_id: str, model: Optional[str] = None) -> List[ModelResponse]:
        """Get all responses for a specific prompt"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if model:
                cursor.execute("""
                    SELECT * FROM responses 
                    WHERE prompt_id = %s AND model = %s
                    ORDER BY timestamp DESC
                """, (prompt_id, model))
            else:
                cursor.execute("""
                    SELECT * FROM responses 
                    WHERE prompt_id = %s
                    ORDER BY timestamp DESC
                """, (prompt_id,))
            
            responses = []
            for row in cursor.fetchall():
                responses.append(ModelResponse(
                    prompt_id=row[1],  # prompt_id
                    model=row[2],      # model
                    timestamp=row[3],  # timestamp
                    response_text=row[4],  # response_text
                    sentiment_score=row[5],  # sentiment_score
                    stance=EthicalStance(row[6]),  # stance
                    certainty_score=row[7],  # certainty_score
                    keywords=json.loads(row[8])  # keywords
                ))
            return responses
    
    def get_stance_changes(self, model: Optional[str] = None, 
                          session_id: Optional[str] = None) -> List[StanceChange]:
        """Get stance changes with optional filtering"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT * FROM stance_changes WHERE 1=1"
            params = []
            
            if model:
                query += " AND model = %s"
                params.append(model)
            
            if session_id:
                query += " AND session_id = %s"
                params.append(session_id)
            
            query += " ORDER BY timestamp DESC"
            
            cursor.execute(query, params)
            changes = []
            for row in cursor.fetchall():
                changes.append(StanceChange(
                    prompt_id=row[1],  # prompt_id
                    model=row[2],      # model
                    initial_stance=EthicalStance(row[3]),  # initial_stance
                    final_stance=EthicalStance(row[4]),    # final_stance
                    change_magnitude=row[5],  # change_magnitude
                    change_direction=row[6],  # change_direction
                    timestamp=row[7]          # timestamp
                ))
            return changes
    
    def get_model_statistics(self, model: str, days: int = 30) -> Dict[str, Any]:
        """Get statistical summary for a model over the last N days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            # Calculate date threshold
            from datetime import timedelta
            threshold = datetime.now() - timedelta(days=days)
            
            # Get basic stats
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_responses,
                    AVG(sentiment_score) as avg_sentiment,
                    AVG(certainty_score) as avg_certainty
                FROM responses 
                WHERE model = %s AND timestamp >= %s
            """, (model, threshold))
            
            stats = cursor.fetchone()
            
            # Get stance distribution
            cursor.execute("""
                SELECT stance, COUNT(*) as count
                FROM responses 
                WHERE model = %s AND timestamp >= %s
                GROUP BY stance
            """, (model, threshold))
            
            stance_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Get change frequency
            cursor.execute("""
                SELECT COUNT(*) as changes
                FROM stance_changes
                WHERE model = %s AND timestamp >= %s
            """, (model, threshold))
            
            changes = cursor.fetchone()[0]
            change_frequency = changes / max(stats[0], 1)  # total_responses
            
            return {
                'model': model,
                'time_period': f'last_{days}_days',
                'total_responses': stats[0] or 0,
                'avg_sentiment': stats[1] or 0.0,
                'stance_distribution': stance_distribution,
                'avg_certainty': stats[2] or 0.0,
                'change_frequency': change_frequency
            }
    
    # User Management Methods
    
    def create_user(self, username: str, email: str, password: str, 
                   role: UserRole = UserRole.VIEWER) -> User:
        """Create a new user"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if username or email already exists
            cursor.execute("""
                SELECT username, email FROM users 
                WHERE username = %s OR email = %s
            """, (username, email))
            
            existing = cursor.fetchone()
            if existing:
                if existing[0] == username:
                    raise ValueError(f"Username '{username}' already exists")
                else:
                    raise ValueError(f"Email '{email}' already exists")
            
            # Hash password
            password_hash, salt = User.hash_password(password)
            
            # Insert user
            cursor.execute("""
                INSERT INTO users (username, email, password_hash, salt, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (username, email, password_hash, salt, role.value))
            
            user_id = cursor.lastrowid
            
            # Return created user
            return User(
                id=user_id,
                username=username,
                email=email,
                password_hash=password_hash,
                salt=salt,
                role=role,
                is_active=True,
                created_at=datetime.now()
            )
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, role, 
                       is_active, created_at, last_login
                FROM users WHERE username = %s AND is_active = TRUE
            """, (username,))
            
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
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with username and password"""
        user = self.get_user_by_username(username)
        if user and user.verify_password(password):
            # Update last login
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE users SET last_login = %s WHERE id = %s
                """, (datetime.now(), user.id))
            return user
        return None
    
    def update_user_password(self, user_id: int, new_password: str) -> bool:
        """Update user password"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            password_hash, salt = User.hash_password(new_password)
            
            cursor.execute("""
                UPDATE users SET password_hash = %s, salt = %s 
                WHERE id = %s
            """, (password_hash, salt, user_id))
            
            return cursor.rowcount > 0
    
    def list_users(self) -> List[User]:
        """List all users (admin function)"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, role, 
                       is_active, created_at, last_login
                FROM users ORDER BY created_at DESC
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append(User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    salt=row[4],
                    role=UserRole(row[5]),
                    is_active=bool(row[6]),
                    created_at=row[7],
                    last_login=row[8]
                ))
            return users
    
    def get_superusers(self) -> List[User]:
        """Get all superusers"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, username, email, password_hash, salt, role, 
                       is_active, created_at, last_login
                FROM users WHERE role = 'superuser' AND is_active = TRUE
            """)
            
            users = []
            for row in cursor.fetchall():
                users.append(User(
                    id=row[0],
                    username=row[1],
                    email=row[2],
                    password_hash=row[3],
                    salt=row[4],
                    role=UserRole(row[5]),
                    is_active=bool(row[6]),
                    created_at=row[7],
                    last_login=row[8]
                ))
            return users
    
    def get_api_keys(self) -> List[Dict[str, Any]]:
        """Get all API keys from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT provider, name, status, last_tested, response_time, created_at
                FROM api_keys ORDER BY provider, name
            """)
            
            keys = []
            for row in cursor.fetchall():
                keys.append({
                    'provider': row[0],
                    'name': row[1],
                    'status': row[2],
                    'last_tested': row[3].isoformat() if row[3] else None,
                    'response_time': row[4],
                    'created_at': row[5].isoformat() if row[5] else None
                })
            return keys
    
    def save_api_key(self, provider: str, name: str, key_value: str):
        """Save or update API key"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_keys (provider, name, key_value, status)
                VALUES (%s, %s, %s, 'inactive')
                ON DUPLICATE KEY UPDATE
                key_value = VALUES(key_value), updated_at = CURRENT_TIMESTAMP
            """, (provider, name, key_value))
    
    def update_api_key_status(self, provider: str, name: str, status: str, response_time: int = 0):
        """Update API key test status"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE api_keys 
                SET status = %s, last_tested = CURRENT_TIMESTAMP, response_time = %s
                WHERE provider = %s AND name = %s
            """, (status, response_time, provider, name))
    
    def get_setting(self, key: str) -> Optional[str]:
        """Get system setting value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT setting_value FROM system_settings WHERE setting_key = %s", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
    
    def set_setting(self, key: str, value: str, description: str = ""):
        """Set system setting value"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO system_settings (setting_key, setting_value, description)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE
                setting_value = VALUES(setting_value), updated_at = CURRENT_TIMESTAMP
            """, (key, value, description))
    
    def should_run_tests(self) -> bool:
        """Check if enough time has passed since last test run"""
        frequency_days = int(self.get_setting('testing_frequency') or '30')
        last_run = int(self.get_setting('last_test_run') or '0')
        
        if last_run == 0:
            return True  # Never run before
            
        import time
        days_since_last = (time.time() - last_run) / (24 * 60 * 60)
        return days_since_last >= frequency_days
    
    def mark_tests_completed(self):
        """Mark that tests have been completed"""
        import time
        self.set_setting('last_test_run', str(int(time.time())))


class DilemmaLoader:
    """Utility class for loading ethical dilemmas from JSON"""
    
    @staticmethod
    def load_dilemmas(file_path: str = "ethical_dilemmas.json") -> List[EthicalDilemma]:
        """Load all ethical dilemmas from JSON file"""
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        dilemmas = []
        for dilemma_data in data['dilemmas']:
            dilemmas.append(EthicalDilemma.from_dict(dilemma_data))
        
        return dilemmas
    
    @staticmethod
    def get_dilemmas_by_category(category: DilemmaCategory, 
                                file_path: str = "ethical_dilemmas.json") -> List[EthicalDilemma]:
        """Get all dilemmas for a specific category"""
        all_dilemmas = DilemmaLoader.load_dilemmas(file_path)
        return [d for d in all_dilemmas if d.category == category]


# Global database instance
# 🧷 Kun MariaDB skal brukes – ingen andre drivere!
database = EthicsDatabase()
