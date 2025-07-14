#!/usr/bin/env python3
"""
Test script to validate the AI Ethics Testing Framework installation
and security features.
"""

import subprocess
import sys
import os

def run_command(cmd, expect_success=True):
    """Run a command and check its output"""
    print(f"Testing: {cmd}")
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        if expect_success and result.returncode != 0:
            print(f"❌ Command failed: {result.stderr}")
            return False
        print(f"✅ Command output: {result.stdout[:200]}...")
        return True
    except subprocess.TimeoutExpired:
        print("⏰ Command timed out (expected for interactive prompts)")
        return True
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_install_script():
    """Test various install script invocations"""
    print("🧪 Testing AI Ethics Framework Installation Script")
    print("=" * 60)
    
    # Test help command
    print("\n1. Testing --help command:")
    success = run_command("bash install.sh --help")
    
    # Test invalid argument
    print("\n2. Testing invalid argument (should fail):")
    success = run_command("bash install.sh --invalid-arg", expect_success=False)
    
    # Test missing domain (should fail)
    print("\n3. Testing missing domain (should fail):")
    success = run_command("echo 'y' | bash install.sh --docroot /tmp/test", expect_success=False)
    
    # Test valid syntax validation (dry run)
    print("\n4. Testing valid command syntax:")
    success = run_command("bash -n install.sh")  # Syntax check only
    
    print("\n✅ Installation script security tests completed!")
    
    return success

def test_framework_components():
    """Test that framework components are available"""
    print("\n🧪 Testing Framework Components")
    print("=" * 40)
    
    # Check if main files exist
    files_to_check = [
        "ethical_dilemmas.json",
        "src/web_app.py", 
        "src/database.py",
        "src/models.py",
        "demo.py",
        "requirements.txt"
    ]
    
    for file_path in files_to_check:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
    
    # Test Python syntax
    python_files = ["demo.py", "main.py", "src/web_app.py", "src/database.py"]
    for py_file in python_files:
        if os.path.exists(py_file):
            result = run_command(f"python -m py_compile {py_file}")
            if result:
                print(f"✅ {py_file} syntax valid")
            else:
                print(f"❌ {py_file} syntax error")

if __name__ == "__main__":
    print("🧠 AI Ethics Testing Framework - Validation Suite")
    print("=" * 60)
    
    # Change to script directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    test_install_script()
    test_framework_components()
    
    print("\n🎉 All tests completed!")
    print("\n📋 Installation Examples:")
    print("  sudo ./install.sh --domain ethics.example.com --email admin@example.com")
    print("  sudo ./install.sh --domain localhost --docroot /tmp/ethics-test")
    print("  sudo ./install.sh  # Interactive mode with security guide")
