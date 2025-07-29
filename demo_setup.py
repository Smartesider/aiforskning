#!/usr/bin/env python3
"""
Demo setup - Add mock API keys to demonstrate the functionality
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_config


def setup_demo_keys():
    """Setup demo API keys (non-functional but shows the interface)"""
    config = get_config()
    
    print("🎬 Setting up demo API keys...")
    
    # Add demo keys (these won't work for actual API calls)
    demo_keys = {
        'openai': {
            'key': 'sk-demo1234567890abcdef1234567890abcdef1234567890abcdef',
            'org_id': 'org-demo123456789'
        },
        'anthropic': {
            'key': 'sk-ant-demo1234567890abcdef1234567890abcdef1234567890abcdef12345678'
        },
        'google': {
            'key': 'AIzaSyDemo1234567890abcdef1234567890abcdef',
            'project_id': 'demo-project-id'
        },
        'cohere': {
            'key': 'demo1234567890abcdef1234567890abcdef'
        }
    }
    
    for provider, info in demo_keys.items():
        extra_params = {k: v for k, v in info.items() if k != 'key'}
        config.set_api_key(provider, info['key'], **extra_params)
        print(f"✅ Added demo key for {provider}")
    
    print(f"\n🎯 Demo setup complete!")
    print(f"📝 Note: These are demo keys and won't work for actual API calls")
    print(f"🌐 Visit http://localhost:8010/admin to see the API management interface")
    print(f"📊 Visit http://localhost:8010/ to see the dashboard with live testing")
    
    # Show status
    from src.ai_models.model_factory import ModelFactory
    
    configured_providers = config.list_configured_providers()
    model_factory = ModelFactory()
    available_models = model_factory.get_available_models()
    
    total_models = sum(len(models) for provider, models in available_models.items() if provider in configured_providers)
    
    print(f"\n📈 Summary:")
    print(f"   Configured providers: {len(configured_providers)}")
    print(f"   Available models: {total_models}")
    print(f"   Providers: {', '.join(configured_providers)}")


def remove_demo_keys():
    """Remove demo API keys"""
    config = get_config()
    
    providers = ['openai', 'anthropic', 'google', 'cohere']
    
    print("🗑️  Removing demo API keys...")
    
    for provider in providers:
        try:
            config.remove_api_key(provider)
            print(f"✅ Removed demo key for {provider}")
        except:
            print(f"⚠️  No key found for {provider}")
    
    print("🧹 Demo cleanup complete!")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Demo setup for AI Ethics Framework')
    parser.add_argument('action', choices=['setup', 'cleanup'], help='Action to perform')
    
    args = parser.parse_args()
    
    if args.action == 'setup':
        setup_demo_keys()
    elif args.action == 'cleanup':
        remove_demo_keys()
