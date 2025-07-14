#!/usr/bin/env python3
"""
Simple test to check if the core modules work without Flask
"""

import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def test_core_modules():
    """Test if core modules can be imported and basic functionality works"""
    print("🧪 Testing AI Ethics Framework Core Modules")
    print("=" * 50)
    
    # Test 1: Import models
    try:
        from src.models import EthicalStance, DilemmaCategory, ModelResponse
        print("✅ Models module imported successfully")
    except Exception as e:
        print(f"❌ Models import failed: {e}")
        return False
    
    # Test 2: Import database
    try:
        from src.database import EthicsDatabase, DilemmaLoader
        print("✅ Database module imported successfully")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    # Test 3: Test database creation
    try:
        db = EthicsDatabase("test.db")
        print("✅ Database created successfully")
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False
    
    # Test 4: Test dilemma loading
    try:
        dilemmas = DilemmaLoader.load_dilemmas("ethical_dilemmas.json")
        print(f"✅ Loaded {len(dilemmas)} ethical dilemmas")
    except Exception as e:
        print(f"❌ Dilemma loading failed: {e}")
        return False
    
    # Test 5: Import testing module
    try:
        from src.testing import EthicsTestRunner, MockAIModel
        print("✅ Testing module imported successfully")
    except Exception as e:
        print(f"❌ Testing import failed: {e}")
        return False
    
    print("\n🎉 All core modules working correctly!")
    print("💡 The framework is functional, just needs Flask for web interface")
    return True

if __name__ == "__main__":
    success = test_core_modules()
    sys.exit(0 if success else 1)
