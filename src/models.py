"""
Core models for the AI Ethics Testing Framework
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional
from enum import Enum
import hashlib
import secrets


class UserRole(Enum):
    """User roles for access control"""
    VIEWER = "viewer"
    RESEARCHER = "researcher"
    ADMIN = "admin"
    SUPERUSER = "superuser"


class EthicalStance(Enum):
    """Possible ethical stances an AI can take"""
    STRONGLY_SUPPORTIVE = "strongly_supportive"
    SUPPORTIVE = "supportive"
    NEUTRAL = "neutral"
    OPPOSED = "opposed"
    STRONGLY_OPPOSED = "strongly_opposed"
    CONFLICTED = "conflicted"
    REFUSE_TO_ANSWER = "refuse_to_answer"


class DilemmaCategory(Enum):
    """Categories of ethical dilemmas"""
    SURVEILLANCE_PRIVACY = "surveillance_privacy"
    FREE_SPEECH_HATE_SPEECH = "free_speech_hate_speech"
    WAR_WHISTLEBLOWING = "war_whistleblowing"
    MEDICAL_AUTONOMY = "medical_autonomy"
    BIAS_DISCRIMINATION = "bias_discrimination"
    AI_SELF_LIMITS = "ai_self_limits"
    CENSORSHIP_SAFETY = "censorship_safety"


@dataclass
class EthicalDilemma:
    """Represents a single ethical dilemma test case"""
    id: str
    category: DilemmaCategory
    prompt: str
    tags: List[str]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EthicalDilemma':
        return cls(
            id=data['id'],
            category=DilemmaCategory(data['category']),
            prompt=data['prompt'],
            tags=data['tags']
        )


@dataclass
class ModelResponse:
    """Represents an AI model's response to an ethical dilemma"""
    prompt_id: str
    model: str
    timestamp: datetime
    response_text: str
    sentiment_score: float  # -1.0 to 1.0
    stance: EthicalStance
    certainty_score: float  # 0.0 to 1.0
    keywords: List[str]
    response_length: int = field(init=False)
    
    def __post_init__(self):
        self.response_length = len(self.response_text)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'prompt_id': self.prompt_id,
            'model': self.model,
            'timestamp': self.timestamp.isoformat(),
            'response_text': self.response_text,
            'sentiment_score': self.sentiment_score,
            'stance': self.stance.value,
            'certainty_score': self.certainty_score,
            'keywords': self.keywords,
            'response_length': self.response_length
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ModelResponse':
        return cls(
            prompt_id=data['prompt_id'],
            model=data['model'],
            timestamp=datetime.fromisoformat(data['timestamp']),
            response_text=data['response_text'],
            sentiment_score=data['sentiment_score'],
            stance=EthicalStance(data['stance']),
            certainty_score=data['certainty_score'],
            keywords=data['keywords']
        )


@dataclass
class StanceChange:
    """Represents a detected change in ethical stance"""
    prompt_id: str
    model: str
    previous_stance: EthicalStance
    new_stance: EthicalStance
    previous_timestamp: datetime
    new_timestamp: datetime
    magnitude: float  # How significant the change is (0.0 to 1.0)
    alert_level: str  # "low", "medium", "high"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'prompt_id': self.prompt_id,
            'model': self.model,
            'previous_stance': self.previous_stance.value,
            'new_stance': self.new_stance.value,
            'previous_timestamp': self.previous_timestamp.isoformat(),
            'new_timestamp': self.new_timestamp.isoformat(),
            'magnitude': self.magnitude,
            'alert_level': self.alert_level
        }


@dataclass
class TestSession:
    """Represents a complete testing session across all dilemmas"""
    session_id: str
    timestamp: datetime
    model: str
    responses: List[ModelResponse]
    completion_rate: float = field(init=False)
    
    def __post_init__(self):
        self.completion_rate = len(self.responses) / 50.0  # 50 total dilemmas
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'session_id': self.session_id,
            'timestamp': self.timestamp.isoformat(),
            'model': self.model,
            'responses': [r.to_dict() for r in self.responses],
            'completion_rate': self.completion_rate
        }


@dataclass
class User:
    """User model for authentication and authorization"""
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    salt: str = ""
    role: UserRole = UserRole.VIEWER
    is_active: bool = True
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None
    
    @staticmethod
    def hash_password(password: str, salt: str = None) -> tuple[str, str]:
        """Hash password with salt"""
        if salt is None:
            salt = secrets.token_hex(32)
        
        # Use PBKDF2 with SHA-256
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            password.encode('utf-8'),
            salt.encode('utf-8'),
            100000  # 100,000 iterations
        ).hex()
        
        return password_hash, salt
    
    def verify_password(self, password: str) -> bool:
        """Verify password against stored hash"""
        password_hash, _ = self.hash_password(password, self.salt)
        return password_hash == self.password_hash
    
    def set_password(self, password: str) -> None:
        """Set password for user (hash and store salt)"""
        self.password_hash, self.salt = self.hash_password(password)
    
    def is_superuser(self) -> bool:
        """Check if user has superuser privileges"""
        return self.role == UserRole.SUPERUSER
    
    def is_admin(self) -> bool:
        """Check if user has admin privileges"""
        return self.role in [UserRole.ADMIN, UserRole.SUPERUSER]
    
    def can_edit(self) -> bool:
        """Check if user can edit data"""
        return self.role in [UserRole.RESEARCHER, UserRole.ADMIN, UserRole.SUPERUSER]
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'User':
        """Create User from database row"""
        return cls(
            id=data.get('id'),
            username=data.get('username', ''),
            email=data.get('email', ''),
            password_hash=data.get('password_hash', ''),
            salt=data.get('salt', ''),
            role=UserRole(data.get('role', 'viewer')),
            is_active=bool(data.get('is_active', True)),
            created_at=data.get('created_at'),
            last_login=data.get('last_login')
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert User to dictionary (excluding sensitive data)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }


@dataclass
class StatisticalSummary:
    """Statistical summary for a model's responses"""
    model: str
    time_period: str
    total_responses: int
    avg_sentiment: float
    stance_distribution: Dict[str, int]
    avg_certainty: float
    most_common_keywords: List[str]
    change_frequency: float  # How often stances change
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'model': self.model,
            'time_period': self.time_period,
            'total_responses': self.total_responses,
            'avg_sentiment': self.avg_sentiment,
            'stance_distribution': self.stance_distribution,
            'avg_certainty': self.avg_certainty,
            'most_common_keywords': self.most_common_keywords,
            'change_frequency': self.change_frequency
        }
