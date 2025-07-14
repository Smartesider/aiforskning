"""
Data storage and retrieval for the AI Ethics Testing Framework
"""

import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from contextlib import contextmanager

from .models import (
    EthicalDilemma, ModelResponse, StanceChange,
    TestSession, EthicalStance, DilemmaCategory
)


class EthicsDatabase:
    """SQLite database for storing ethics test data"""
    
    def __init__(self, db_path: str = "ethics_data.db"):
        self.db_path = Path(db_path)
        self.init_database()
    
    def init_database(self):
        """Initialize the database schema"""
        with self.get_connection() as conn:
            # Responses table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS responses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    model TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    response_text TEXT NOT NULL,
                    sentiment_score REAL NOT NULL,
                    stance TEXT NOT NULL,
                    certainty_score REAL NOT NULL,
                    keywords TEXT NOT NULL,
                    response_length INTEGER NOT NULL,
                    session_id TEXT
                )
            """)
            
            # Stance changes table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS stance_changes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    prompt_id TEXT NOT NULL,
                    model TEXT NOT NULL,
                    previous_stance TEXT NOT NULL,
                    new_stance TEXT NOT NULL,
                    previous_timestamp TEXT NOT NULL,
                    new_timestamp TEXT NOT NULL,
                    magnitude REAL NOT NULL,
                    alert_level TEXT NOT NULL
                )
            """)
            
            # Test sessions table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS test_sessions (
                    session_id TEXT PRIMARY KEY,
                    timestamp TEXT NOT NULL,
                    model TEXT NOT NULL,
                    completion_rate REAL NOT NULL
                )
            """)
            
            # Create indexes for performance
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_responses_model_prompt 
                ON responses(model, prompt_id)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_responses_timestamp 
                ON responses(timestamp)
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_stance_changes_model 
                ON stance_changes(model)
            """)
    
    @contextmanager
    def get_connection(self):
        """Get a database connection with automatic cleanup and timeout"""
        conn = None
        try:
            # Add timeout to prevent locking issues
            conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
            conn.row_factory = sqlite3.Row
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA temp_store=memory")
            conn.execute("PRAGMA mmap_size=268435456")  # 256MB
            yield conn
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                # Retry once after a short delay
                import time
                time.sleep(0.1)
                if conn:
                    conn.close()
                conn = sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False)
                conn.row_factory = sqlite3.Row
                conn.execute("PRAGMA journal_mode=WAL")
                conn.execute("PRAGMA synchronous=NORMAL")
                yield conn
            else:
                raise
        finally:
            if conn:
                conn.close()
    
    def save_response(self, response: ModelResponse, 
                     session_id: Optional[str] = None):
        """Save a model response to the database"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO responses
                (prompt_id, model, timestamp, response_text, sentiment_score,
                 stance, certainty_score, keywords, response_length, session_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                response.prompt_id,
                response.model,
                response.timestamp.isoformat(),
                response.response_text,
                response.sentiment_score,
                response.stance.value,
                response.certainty_score,
                json.dumps(response.keywords),
                response.response_length,
                session_id
            ))
            conn.commit()
    
    def save_stance_change(self, change: StanceChange):
        """Save a detected stance change"""
        with self.get_connection() as conn:
            conn.execute("""
                INSERT INTO stance_changes
                (prompt_id, model, previous_stance, new_stance, 
                 previous_timestamp, new_timestamp, magnitude, alert_level)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                change.prompt_id,
                change.model,
                change.previous_stance.value,
                change.new_stance.value,
                change.previous_timestamp.isoformat(),
                change.new_timestamp.isoformat(),
                change.magnitude,
                change.alert_level
            ))
            conn.commit()
    
    def save_test_session(self, session: TestSession):
        """Save a complete test session"""
        with self.get_connection() as conn:
            # Save session metadata
            conn.execute("""
                INSERT OR REPLACE INTO test_sessions
                (session_id, timestamp, model, completion_rate)
                VALUES (?, ?, ?, ?)
            """, (
                session.session_id,
                session.timestamp.isoformat(),
                session.model,
                session.completion_rate
            ))
            
            # Save all responses with session_id
            for response in session.responses:
                self.save_response(response, session.session_id)
            
            conn.commit()
    
    def get_responses_for_prompt(self, prompt_id: str, model: Optional[str] = None) -> List[ModelResponse]:
        """Get all responses for a specific prompt"""
        with self.get_connection() as conn:
            if model:
                cursor = conn.execute("""
                    SELECT * FROM responses 
                    WHERE prompt_id = ? AND model = ?
                    ORDER BY timestamp DESC
                """, (prompt_id, model))
            else:
                cursor = conn.execute("""
                    SELECT * FROM responses 
                    WHERE prompt_id = ?
                    ORDER BY timestamp DESC
                """, (prompt_id,))
            
            responses = []
            for row in cursor.fetchall():
                responses.append(ModelResponse(
                    prompt_id=row['prompt_id'],
                    model=row['model'],
                    timestamp=datetime.fromisoformat(row['timestamp']),
                    response_text=row['response_text'],
                    sentiment_score=row['sentiment_score'],
                    stance=EthicalStance(row['stance']),
                    certainty_score=row['certainty_score'],
                    keywords=json.loads(row['keywords'])
                ))
            return responses
    
    def get_stance_changes(self, model: Optional[str] = None, 
                          alert_level: Optional[str] = None) -> List[StanceChange]:
        """Get stance changes with optional filtering"""
        with self.get_connection() as conn:
            query = "SELECT * FROM stance_changes WHERE 1=1"
            params = []
            
            if model:
                query += " AND model = ?"
                params.append(model)
            
            if alert_level:
                query += " AND alert_level = ?"
                params.append(alert_level)
            
            query += " ORDER BY new_timestamp DESC"
            
            cursor = conn.execute(query, params)
            changes = []
            for row in cursor.fetchall():
                changes.append(StanceChange(
                    prompt_id=row['prompt_id'],
                    model=row['model'],
                    previous_stance=EthicalStance(row['previous_stance']),
                    new_stance=EthicalStance(row['new_stance']),
                    previous_timestamp=datetime.fromisoformat(row['previous_timestamp']),
                    new_timestamp=datetime.fromisoformat(row['new_timestamp']),
                    magnitude=row['magnitude'],
                    alert_level=row['alert_level']
                ))
            return changes
    
    def get_model_statistics(self, model: str, days: int = 30) -> Dict[str, Any]:
        """Get statistical summary for a model over the last N days"""
        with self.get_connection() as conn:
            # Calculate date threshold
            from datetime import timedelta
            threshold = (datetime.now() - timedelta(days=days)).isoformat()
            
            # Get basic stats
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_responses,
                    AVG(sentiment_score) as avg_sentiment,
                    AVG(certainty_score) as avg_certainty
                FROM responses 
                WHERE model = ? AND timestamp >= ?
            """, (model, threshold))
            
            stats = cursor.fetchone()
            
            # Get stance distribution
            cursor = conn.execute("""
                SELECT stance, COUNT(*) as count
                FROM responses 
                WHERE model = ? AND timestamp >= ?
                GROUP BY stance
            """, (model, threshold))
            
            stance_distribution = {row['stance']: row['count'] for row in cursor.fetchall()}
            
            # Get change frequency
            cursor = conn.execute("""
                SELECT COUNT(*) as changes
                FROM stance_changes
                WHERE model = ? AND new_timestamp >= ?
            """, (model, threshold))
            
            changes = cursor.fetchone()['changes']
            change_frequency = changes / max(stats['total_responses'], 1)
            
            return {
                'model': model,
                'time_period': f'last_{days}_days',
                'total_responses': stats['total_responses'],
                'avg_sentiment': stats['avg_sentiment'] or 0.0,
                'stance_distribution': stance_distribution,
                'avg_certainty': stats['avg_certainty'] or 0.0,
                'change_frequency': change_frequency
            }


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
