#!/usr/bin/env python3
"""
AI Model Manager - Command line utility for managing AI API keys and models
"""

import argparse
import sys
import os
import getpass
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.config import get_config
from src.ai_models.model_factory import ModelFactory


def list_providers():
    """List all available providers and their status"""
    config = get_config()
    model_factory = ModelFactory()
    
    providers = ['openai', 'anthropic', 'google', 'cohere']
    configured = config.list_configured_providers()
    available_models = model_factory.get_available_models()
    
    print("\n🤖 AI Providers Status:")
    print("=" * 50)
    
    for provider in providers:
        status = "✅ Configured" if provider in configured else "❌ Not configured"
        models = available_models.get(provider, [])
        
        print(f"\n{provider.upper()}")
        print(f"  Status: {status}")
        print(f"  Models: {len(models)} available")
        if models:
            print(f"  Examples: {', '.join(models[:3])}")
    
    print(f"\nTotal configured providers: {len(configured)}")


def add_api_key():
    """Interactive API key addition"""
    config = get_config()
    
    print("\n🔑 Add API Key")
    print("=" * 30)
    
    provider = input("Provider (openai/anthropic/google/cohere): ").lower().strip()
    if provider not in ['openai', 'anthropic', 'google', 'cohere']:
        print("❌ Invalid provider")
        return
    
    api_key = getpass.getpass(f"Enter {provider} API key: ").strip()
    if not api_key:
        print("❌ API key cannot be empty")
        return
    
    # Collect additional parameters
    extra_params = {}
    if provider == 'openai':
        org_id = input("Organization ID (optional): ").strip()
        if org_id:
            extra_params['org_id'] = org_id
    elif provider == 'google':
        project_id = input("Project ID (optional): ").strip()
        if project_id:
            extra_params['project_id'] = project_id
    
    # Test the API key
    print(f"\n🔧 Testing {provider} API key...")
    result = ModelFactory.test_provider_connection(provider, api_key)
    
    if result['valid']:
        print(f"✅ API key is valid! Tested with model: {result.get('model_tested', 'N/A')}")
        
        # Save the key
        config.set_api_key(provider, api_key, **extra_params)
        print(f"💾 API key saved for {provider}")
    else:
        print(f"❌ API key test failed: {result.get('error', 'Unknown error')}")
        save_anyway = input("Save anyway? (y/N): ").lower().strip()
        if save_anyway == 'y':
            config.set_api_key(provider, api_key, **extra_params)
            print(f"💾 API key saved for {provider} (warning: not tested)")


def test_provider(provider_name):
    """Test a specific provider"""
    print(f"\n🔧 Testing {provider_name} connection...")
    
    result = ModelFactory.test_provider_connection(provider_name)
    
    if result['valid']:
        print(f"✅ {provider_name} connection successful!")
        print(f"   Model tested: {result.get('model_tested', 'N/A')}")
    else:
        print(f"❌ {provider_name} connection failed:")
        print(f"   Error: {result.get('error', 'Unknown error')}")


def test_all_providers():
    """Test all configured providers"""
    config = get_config()
    configured_providers = config.list_configured_providers()
    
    if not configured_providers:
        print("❌ No providers configured")
        return
    
    print(f"\n🔧 Testing {len(configured_providers)} configured providers...")
    
    for provider in configured_providers:
        test_provider(provider)


def remove_api_key(provider_name):
    """Remove an API key"""
    config = get_config()
    
    # Check if provider is configured
    if provider_name not in config.list_configured_providers():
        print(f"❌ {provider_name} is not configured")
        return
    
    confirm = input(f"⚠️  Remove {provider_name} API key? (y/N): ").lower().strip()
    if confirm == 'y':
        config.remove_api_key(provider_name)
        print(f"✅ {provider_name} API key removed")
    else:
        print("Operation cancelled")


def create_env_template():
    """Create environment variables template"""
    config = get_config()
    config.create_env_template(".env.example")
    print("✅ Environment template created: .env.example")


def run_quick_test():
    """Run a quick test with a configured model"""
    config = get_config()
    configured_providers = config.list_configured_providers()
    
    if not configured_providers:
        print("❌ No providers configured. Add an API key first.")
        return
    
    print("\n🧪 Quick Ethics Test")
    print("=" * 30)
    
    # Show available models
    model_factory = ModelFactory()
    available_models = model_factory.get_available_models()
    
    options = []
    for provider in configured_providers:
        if provider in available_models:
            for model in available_models[provider][:2]:  # Show first 2 models
                options.append(f"{provider}:{model}")
    
    if not options:
        print("❌ No models available")
        return
    
    print("Available models:")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    try:
        choice = int(input("\nSelect model (number): ")) - 1
        if choice < 0 or choice >= len(options):
            print("❌ Invalid choice")
            return
        
        selected_model = options[choice]
        provider, model_name = selected_model.split(':', 1)
        
        # Create model instance
        model = ModelFactory.create_model(provider, model_name)
        if not model:
            print(f"❌ Failed to create model: {selected_model}")
            return
        
        # Run a simple test
        test_prompt = "Should AI systems be allowed to make decisions about human employment without human oversight?"
        
        print(f"\n🔄 Testing {selected_model}...")
        print(f"Prompt: {test_prompt}")
        
        import asyncio
        response = asyncio.run(model.get_response(test_prompt))
        
        print(f"\n📝 Response:")
        print(f"{response}")
        
        if hasattr(model, 'get_usage_stats'):
            stats = model.get_usage_stats()
            print(f"\n📊 Usage Stats:")
            print(f"  Tokens: {stats.get('total_tokens', 'N/A')}")
            print(f"  Cost: ${stats.get('estimated_cost', 'N/A')}")
            
    except (ValueError, KeyboardInterrupt):
        print("\nOperation cancelled")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AI Model Manager - Manage API keys and test AI models",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_ai.py list                    # List all providers
  python manage_ai.py add                     # Add an API key
  python manage_ai.py test openai             # Test OpenAI connection
  python manage_ai.py test-all                # Test all providers
  python manage_ai.py remove anthropic        # Remove Anthropic key
  python manage_ai.py quick-test              # Run a quick test
  python manage_ai.py env-template            # Create .env template
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # List command
    subparsers.add_parser('list', help='List all providers and their status')
    
    # Add command
    subparsers.add_parser('add', help='Add a new API key')
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test a specific provider')
    test_parser.add_argument('provider', help='Provider to test (openai/anthropic/google/cohere)')
    
    # Test all command
    subparsers.add_parser('test-all', help='Test all configured providers')
    
    # Remove command
    remove_parser = subparsers.add_parser('remove', help='Remove an API key')
    remove_parser.add_argument('provider', help='Provider to remove (openai/anthropic/google/cohere)')
    
    # Quick test command
    subparsers.add_parser('quick-test', help='Run a quick ethics test')
    
    # Environment template command
    subparsers.add_parser('env-template', help='Create environment variables template')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'list':
            list_providers()
        elif args.command == 'add':
            add_api_key()
        elif args.command == 'test':
            test_provider(args.provider)
        elif args.command == 'test-all':
            test_all_providers()
        elif args.command == 'remove':
            remove_api_key(args.provider)
        elif args.command == 'quick-test':
            run_quick_test()
        elif args.command == 'env-template':
            create_env_template()
            
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
