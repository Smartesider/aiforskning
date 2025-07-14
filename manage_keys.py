#!/usr/bin/env python3
"""
API Key Management CLI for AI Ethics Testing Framework
"""

import argparse
import sys
import os
from getpass import getpass

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import get_config


def list_providers(config):
    """List all configured providers"""
    providers = config.list_configured_providers()
    
    if not providers:
        print("No API keys configured.")
        print("Use 'python manage_keys.py set <provider> <key>' to add keys.")
        return
    
    print("Configured API providers:")
    for provider in providers:
        key = config.get_api_key(provider)
        if key:
            # Mask the key for security
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            valid = "✓" if config.validate_api_key(provider, key) else "✗"
            print(f"  {provider}: {masked_key} {valid}")


def set_api_key(config, provider, key, **kwargs):
    """Set an API key for a provider"""
    if not key:
        key = getpass(f"Enter API key for {provider}: ")
    
    if not key:
        print("No key provided.")
        return
    
    # Validate key format
    if config.validate_api_key(provider, key):
        config.set_api_key(provider, key, **kwargs)
        print(f"✓ API key for {provider} configured successfully.")
    else:
        print(f"⚠ Warning: API key format for {provider} appears invalid.")
        confirm = input("Continue anyway? (y/N): ")
        if confirm.lower() == 'y':
            config.set_api_key(provider, key, **kwargs)
            print(f"✓ API key for {provider} configured.")
        else:
            print("Operation cancelled.")


def remove_api_key(config, provider):
    """Remove an API key for a provider"""
    if config.get_api_key(provider):
        config.remove_api_key(provider)
        print(f"✓ API key for {provider} removed.")
    else:
        print(f"No API key found for {provider}.")


def test_api_key(config, provider):
    """Test an API key"""
    key = config.get_api_key(provider)
    if not key:
        print(f"No API key configured for {provider}.")
        return
    
    valid = config.validate_api_key(provider, key)
    status = "✓ Valid format" if valid else "✗ Invalid format"
    print(f"{provider}: {status}")
    
    # TODO: Add actual API connectivity test
    print("Note: This only validates key format. Add actual API test for connectivity.")


def create_env_file(config):
    """Create .env file with current configuration"""
    config.create_env_template(".env.example")
    print("✓ Created .env.example file with environment variable template.")


def main():
    parser = argparse.ArgumentParser(
        description="Manage API keys for AI Ethics Testing Framework"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List configured API providers')
    
    # Set command
    set_parser = subparsers.add_parser('set', help='Set API key for a provider')
    set_parser.add_argument('provider', help='Provider name (openai, anthropic, google, etc.)')
    set_parser.add_argument('key', nargs='?', help='API key (will prompt if not provided)')
    set_parser.add_argument('--org-id', help='Organization ID (for OpenAI)')
    set_parser.add_argument('--project-id', help='Project ID (for Google)')
    set_parser.add_argument('--endpoint', help='Endpoint URL (for Azure)')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove API key for a provider')
    remove_parser.add_argument('provider', help='Provider name')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test API key validity')
    test_parser.add_argument('provider', help='Provider name')
    
    # Create env command
    subparsers.add_parser('create-env', help='Create .env.example file')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    config = get_config()
    
    if args.command == 'list':
        list_providers(config)
    
    elif args.command == 'set':
        kwargs = {}
        if args.org_id:
            kwargs['org_id'] = args.org_id
        if args.project_id:
            kwargs['project_id'] = args.project_id
        if args.endpoint:
            kwargs['endpoint'] = args.endpoint
        
        set_api_key(config, args.provider, args.key, **kwargs)
    
    elif args.command == 'remove':
        remove_api_key(config, args.provider)
    
    elif args.command == 'test':
        test_api_key(config, args.provider)
    
    elif args.command == 'create-env':
        create_env_file(config)


if __name__ == '__main__':
    main()
