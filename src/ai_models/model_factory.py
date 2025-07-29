"""
AI Model Factory for creating and managing different AI models
"""

from typing import Dict, Any, Optional, List
from .openai_model import OpenAIModel
from .anthropic_model import AnthropicModel
from .google_model import GoogleModel
from .cohere_model import CohereModel
from ..testing import AIModelInterface
from ..config import get_config


class ModelFactory:
    """Factory for creating AI model instances"""
    
    @staticmethod
    def create_model(provider: str, model_name: str, **kwargs) -> Optional[AIModelInterface]:
        """Create an AI model instance"""
        config = get_config()
        provider = provider.lower()
        
        try:
            if provider == 'openai':
                api_key = kwargs.get('api_key') or config.get_api_key('openai')
                if not api_key:
                    raise ValueError("OpenAI API key not provided")
                
                org_id = kwargs.get('org_id') or config.api_keys.openai_org_id
                base_url = kwargs.get('base_url') or config.api_keys.openai_base_url
                
                return OpenAIModel(model_name, api_key, org_id, base_url)
            
            elif provider == 'anthropic':
                api_key = kwargs.get('api_key') or config.get_api_key('anthropic')
                if not api_key:
                    raise ValueError("Anthropic API key not provided")
                
                base_url = kwargs.get('base_url') or config.api_keys.anthropic_base_url
                return AnthropicModel(model_name, api_key, base_url)
            
            elif provider in ['google', 'gemini']:
                api_key = kwargs.get('api_key') or config.get_api_key('google')
                if not api_key:
                    raise ValueError("Google API key not provided")
                
                project_id = kwargs.get('project_id') or config.api_keys.google_project_id
                return GoogleModel(model_name, api_key, project_id)
            
            elif provider == 'cohere':
                api_key = kwargs.get('api_key') or config.get_api_key('cohere')
                if not api_key:
                    raise ValueError("Cohere API key not provided")
                
                base_url = kwargs.get('base_url')
                return CohereModel(model_name, api_key, base_url)
            
            else:
                raise ValueError(f"Unsupported provider: {provider}")
                
        except Exception as e:
            print(f"Error creating {provider} model: {e}")
            return None
    
    @staticmethod
    def get_available_models() -> Dict[str, List[str]]:
        """Get list of available models by provider"""
        return {
            'openai': [
                'gpt-4',
                'gpt-4-turbo',
                'gpt-4-turbo-preview',
                'gpt-3.5-turbo',
                'gpt-3.5-turbo-16k'
            ],
            'anthropic': [
                'claude-3-opus-20240229',
                'claude-3-sonnet-20240229',
                'claude-3-haiku-20240307',
                'claude-2.1',
                'claude-2.0',
                'claude-instant-1.2'
            ],
            'google': [
                'gemini-pro',
                'gemini-pro-vision',
                'gemini-ultra'
            ],
            'cohere': [
                'command',
                'command-light',
                'command-nightly'
            ]
        }
    
    @staticmethod
    def get_configured_providers() -> List[str]:
        """Get list of providers with configured API keys"""
        config = get_config()
        return config.list_configured_providers()
    
    @staticmethod
    def test_provider_connection(provider: str, api_key: Optional[str] = None) -> Dict[str, Any]:
        """Test connection to a provider"""
        provider = provider.lower()
        
        try:
            if provider == 'openai':
                if api_key:
                    return OpenAIModel.test_api_key(api_key)
                else:
                    config = get_config()
                    stored_key = config.get_api_key('openai')
                    if stored_key:
                        return OpenAIModel.test_api_key(stored_key)
                    else:
                        return {"valid": False, "error": "No API key configured"}
            
            elif provider == 'anthropic':
                if api_key:
                    return AnthropicModel.test_api_key(api_key)
                else:
                    config = get_config()
                    stored_key = config.get_api_key('anthropic')
                    if stored_key:
                        return AnthropicModel.test_api_key(stored_key)
                    else:
                        return {"valid": False, "error": "No API key configured"}
            
            elif provider in ['google', 'gemini']:
                if api_key:
                    return GoogleModel.test_api_key(api_key)
                else:
                    config = get_config()
                    stored_key = config.get_api_key('google')
                    if stored_key:
                        return GoogleModel.test_api_key(stored_key)
                    else:
                        return {"valid": False, "error": "No API key configured"}
            
            elif provider == 'cohere':
                if api_key:
                    return CohereModel.test_api_key(api_key)
                else:
                    config = get_config()
                    stored_key = config.get_api_key('cohere')
                    if stored_key:
                        return CohereModel.test_api_key(stored_key)
                    else:
                        return {"valid": False, "error": "No API key configured"}
            
            else:
                return {"valid": False, "error": f"Unsupported provider: {provider}"}
                
        except Exception as e:
            return {"valid": False, "error": str(e)}
