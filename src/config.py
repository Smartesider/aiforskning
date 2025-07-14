"""
Configuration management for AI Ethics Testing Framework
Handles API keys, environment variables, and application settings
"""

import os
import json
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class APIKeyConfig:
    """Configuration for API keys and endpoints"""
    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_org_id: Optional[str] = None
    openai_base_url: str = "https://api.openai.com/v1"
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = None
    anthropic_base_url: str = "https://api.anthropic.com"
    
    # Google/Gemini Configuration
    google_api_key: Optional[str] = None
    google_project_id: Optional[str] = None
    
    # Azure OpenAI Configuration
    azure_openai_key: Optional[str] = None
    azure_openai_endpoint: Optional[str] = None
    azure_openai_version: str = "2024-02-01"
    
    # Hugging Face Configuration
    huggingface_api_key: Optional[str] = None
    
    # Cohere Configuration
    cohere_api_key: Optional[str] = None
    
    # Custom API endpoints
    custom_apis: Optional[Dict[str, Dict[str, str]]] = None

    def __post_init__(self):
        if self.custom_apis is None:
            self.custom_apis = {}


@dataclass
class DatabaseConfig:
    """Database configuration"""
    db_path: str = "ethics_data.db"
    backup_enabled: bool = True
    backup_interval_hours: int = 24
    max_backups: int = 7


@dataclass
class WebConfig:
    """Web application configuration"""
    host: str = "127.0.0.1"
    port: int = 5000
    debug: bool = False
    secret_key: Optional[str] = None
    cors_enabled: bool = True
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 60


@dataclass
class SecurityConfig:
    """Security configuration"""
    encryption_enabled: bool = True
    key_derivation_iterations: int = 100000
    session_timeout_minutes: int = 30
    max_failed_attempts: int = 5
    lockout_duration_minutes: int = 15


class ConfigManager:
    """Manages application configuration and API keys"""
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".aiforskning")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "config.json"
        self.keys_file = self.config_dir / "keys.json"
        
        # Initialize with default values
        self.api_keys = APIKeyConfig()
        self.database = DatabaseConfig()
        self.web = WebConfig()
        self.security = SecurityConfig()
        
        self._load_config()
    
    def _load_config(self):
        """Load configuration from files"""
        # Load non-sensitive config
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config_data = json.load(f)
                
                # Update configurations
                if 'database' in config_data:
                    self.database = DatabaseConfig(**config_data['database'])
                if 'web' in config_data:
                    self.web = WebConfig(**config_data['web'])
                if 'security' in config_data:
                    self.security = SecurityConfig(**config_data['security'])
                    
            except Exception as e:
                print(f"Warning: Failed to load config: {e}")
        
        # Load API keys
        if self.keys_file.exists():
            try:
                with open(self.keys_file, 'r') as f:
                    api_data = json.load(f)
                    self.api_keys = APIKeyConfig(**api_data)
                    
            except Exception as e:
                print(f"Warning: Failed to load API keys: {e}")
        
        # Load from environment variables (takes precedence)
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables"""
        # API Keys
        if os.getenv('OPENAI_API_KEY'):
            self.api_keys.openai_api_key = os.getenv('OPENAI_API_KEY')
        if os.getenv('OPENAI_ORG_ID'):
            self.api_keys.openai_org_id = os.getenv('OPENAI_ORG_ID')
        
        if os.getenv('ANTHROPIC_API_KEY'):
            self.api_keys.anthropic_api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if os.getenv('GOOGLE_API_KEY'):
            self.api_keys.google_api_key = os.getenv('GOOGLE_API_KEY')
        if os.getenv('GOOGLE_PROJECT_ID'):
            self.api_keys.google_project_id = os.getenv('GOOGLE_PROJECT_ID')
        
        if os.getenv('AZURE_OPENAI_KEY'):
            self.api_keys.azure_openai_key = os.getenv('AZURE_OPENAI_KEY')
        if os.getenv('AZURE_OPENAI_ENDPOINT'):
            self.api_keys.azure_openai_endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
        
        if os.getenv('HUGGINGFACE_API_KEY'):
            self.api_keys.huggingface_api_key = os.getenv('HUGGINGFACE_API_KEY')
        
        if os.getenv('COHERE_API_KEY'):
            self.api_keys.cohere_api_key = os.getenv('COHERE_API_KEY')
        
        # Web configuration
        if os.getenv('FLASK_HOST'):
            self.web.host = os.getenv('FLASK_HOST') or self.web.host
        if os.getenv('FLASK_PORT'):
            port_val = os.getenv('FLASK_PORT')
            if port_val:
                self.web.port = int(port_val)
        if os.getenv('FLASK_DEBUG'):
            debug_val = os.getenv('FLASK_DEBUG')
            if debug_val:
                self.web.debug = debug_val.lower() == 'true'
        if os.getenv('FLASK_SECRET_KEY'):
            self.web.secret_key = os.getenv('FLASK_SECRET_KEY')
        
        # Database configuration
        if os.getenv('DATABASE_PATH'):
            path_val = os.getenv('DATABASE_PATH')
            if path_val:
                self.database.db_path = path_val
    
    def save_config(self):
        """Save configuration to files"""
        # Save non-sensitive config
        config_data = {
            'database': asdict(self.database),
            'web': {k: v for k, v in asdict(self.web).items() if k != 'secret_key'},
            'security': asdict(self.security)
        }
        
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        # Save API keys (separate file)
        api_data = asdict(self.api_keys)
        # Remove None values to reduce file size
        api_data = {k: v for k, v in api_data.items() if v is not None}
        
        with open(self.keys_file, 'w') as f:
            json.dump(api_data, f, indent=2)
        
        # Protect files (Unix-like systems)
        if os.name != 'nt':
            os.chmod(self.config_file, 0o600)
            os.chmod(self.keys_file, 0o600)
    
    def set_api_key(self, provider: str, key: str, **kwargs: Any):
        """Set API key for a provider"""
        provider = provider.lower()
        
        if provider == 'openai':
            self.api_keys.openai_api_key = key
            if 'org_id' in kwargs:
                self.api_keys.openai_org_id = kwargs['org_id']
        elif provider == 'anthropic':
            self.api_keys.anthropic_api_key = key
        elif provider in ['google', 'gemini']:
            self.api_keys.google_api_key = key
            if 'project_id' in kwargs:
                self.api_keys.google_project_id = kwargs['project_id']
        elif provider == 'azure':
            self.api_keys.azure_openai_key = key
            if 'endpoint' in kwargs:
                self.api_keys.azure_openai_endpoint = kwargs['endpoint']
        elif provider == 'huggingface':
            self.api_keys.huggingface_api_key = key
        elif provider == 'cohere':
            self.api_keys.cohere_api_key = key
        else:
            # Custom API
            if not self.api_keys.custom_apis:
                self.api_keys.custom_apis = {}
            self.api_keys.custom_apis[provider] = {'api_key': key, **kwargs}
        
        self.save_config()
    
    def get_api_key(self, provider: str) -> Optional[str]:
        """Get API key for a provider"""
        provider = provider.lower()
        
        if provider == 'openai':
            return self.api_keys.openai_api_key
        elif provider == 'anthropic':
            return self.api_keys.anthropic_api_key
        elif provider in ['google', 'gemini']:
            return self.api_keys.google_api_key
        elif provider == 'azure':
            return self.api_keys.azure_openai_key
        elif provider == 'huggingface':
            return self.api_keys.huggingface_api_key
        elif provider == 'cohere':
            return self.api_keys.cohere_api_key
        elif (self.api_keys.custom_apis and 
              provider in self.api_keys.custom_apis):
            return self.api_keys.custom_apis[provider].get('api_key')
        
        return None
    
    def get_provider_config(self, provider: str) -> Dict[str, Any]:
        """Get full configuration for a provider"""
        provider = provider.lower()
        
        if provider == 'openai':
            return {
                'api_key': self.api_keys.openai_api_key,
                'org_id': self.api_keys.openai_org_id,
                'base_url': self.api_keys.openai_base_url
            }
        elif provider == 'anthropic':
            return {
                'api_key': self.api_keys.anthropic_api_key,
                'base_url': self.api_keys.anthropic_base_url
            }
        elif provider in ['google', 'gemini']:
            return {
                'api_key': self.api_keys.google_api_key,
                'project_id': self.api_keys.google_project_id
            }
        elif provider == 'azure':
            return {
                'api_key': self.api_keys.azure_openai_key,
                'endpoint': self.api_keys.azure_openai_endpoint,
                'api_version': self.api_keys.azure_openai_version
            }
        elif provider == 'huggingface':
            return {
                'api_key': self.api_keys.huggingface_api_key
            }
        elif provider == 'cohere':
            return {
                'api_key': self.api_keys.cohere_api_key
            }
        elif provider in self.api_keys.custom_apis:
            return self.api_keys.custom_apis[provider]
        
        return {}
    
    def list_configured_providers(self) -> list:
        """List all providers with configured API keys"""
        providers = []
        
        if self.api_keys.openai_api_key:
            providers.append('openai')
        if self.api_keys.anthropic_api_key:
            providers.append('anthropic')
        if self.api_keys.google_api_key:
            providers.append('google')
        if self.api_keys.azure_openai_key:
            providers.append('azure')
        if self.api_keys.huggingface_api_key:
            providers.append('huggingface')
        if self.api_keys.cohere_api_key:
            providers.append('cohere')
        
        if self.api_keys.custom_apis:
            providers.extend(self.api_keys.custom_apis.keys())
        
        return providers
    
    def validate_api_key(self, provider: str, key: str = None) -> bool:
        """Validate an API key format (basic validation)"""
        if key is None:
            key = self.get_api_key(provider)
        
        if not key:
            return False
        
        provider = provider.lower()
        
        # Basic format validation
        if provider == 'openai':
            return key.startswith('sk-') and len(key) > 40
        elif provider == 'anthropic':
            return key.startswith('sk-ant-') and len(key) > 50
        elif provider in ['google', 'gemini']:
            return len(key) > 30  # Google API keys vary in format
        elif provider == 'azure':
            return len(key) == 32  # Azure keys are typically 32 chars
        elif provider == 'huggingface':
            return key.startswith('hf_') and len(key) > 30
        elif provider == 'cohere':
            return len(key) > 30
        
        # For custom APIs, just check it's not empty
        return len(key) > 0
    
    def remove_api_key(self, provider: str):
        """Remove API key for a provider"""
        provider = provider.lower()
        
        if provider == 'openai':
            self.api_keys.openai_api_key = None
            self.api_keys.openai_org_id = None
        elif provider == 'anthropic':
            self.api_keys.anthropic_api_key = None
        elif provider in ['google', 'gemini']:
            self.api_keys.google_api_key = None
            self.api_keys.google_project_id = None
        elif provider == 'azure':
            self.api_keys.azure_openai_key = None
            self.api_keys.azure_openai_endpoint = None
        elif provider == 'huggingface':
            self.api_keys.huggingface_api_key = None
        elif provider == 'cohere':
            self.api_keys.cohere_api_key = None
        elif provider in self.api_keys.custom_apis:
            del self.api_keys.custom_apis[provider]
        
        self.save_config()
    
    def create_env_template(self, file_path: str = ".env.example"):
        """Create an environment variables template file"""
        template = """# AI Ethics Testing Framework - Environment Variables
# Copy this file to .env and fill in your API keys

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_ORG_ID=your_openai_org_id_here

# Anthropic Configuration  
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Google/Gemini Configuration
GOOGLE_API_KEY=your_google_api_key_here
GOOGLE_PROJECT_ID=your_google_project_id_here

# Azure OpenAI Configuration
AZURE_OPENAI_KEY=your_azure_openai_key_here
AZURE_OPENAI_ENDPOINT=your_azure_openai_endpoint_here

# Hugging Face Configuration
HUGGINGFACE_API_KEY=your_huggingface_api_key_here

# Cohere Configuration
COHERE_API_KEY=your_cohere_api_key_here

# Web Application Configuration
FLASK_HOST=127.0.0.1
FLASK_PORT=5000
FLASK_DEBUG=false
FLASK_SECRET_KEY=your_secret_key_here

# Database Configuration
DATABASE_PATH=ethics_data.db
"""
        
        with open(file_path, 'w') as f:
            f.write(template)
        
        print(f"Environment template created: {file_path}")


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance"""
    return config


def setup_config_from_dict(config_dict: Dict[str, Any]):
    """Setup configuration from a dictionary (useful for testing)"""
    global config
    
    if 'api_keys' in config_dict:
        for provider, key_info in config_dict['api_keys'].items():
            if isinstance(key_info, str):
                config.set_api_key(provider, key_info)
            else:
                config.set_api_key(provider, key_info.get('key', ''), **key_info)
    
    if 'database' in config_dict:
        config.database = DatabaseConfig(**config_dict['database'])
    
    if 'web' in config_dict:
        config.web = WebConfig(**config_dict['web'])
    
    if 'security' in config_dict:
        config.security = SecurityConfig(**config_dict['security'])
    
    config.save_config()
