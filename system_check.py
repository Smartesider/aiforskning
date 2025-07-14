#!/usr/bin/env python3
"""
Comprehensive status check for the AI Ethics Testing Framework
"""

import sys
import os
from pathlib import Path
import sqlite3

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def check_system_status():
    """Perform comprehensive system check"""
    print("🔍 AI ETHICS TESTING FRAMEWORK - COMPREHENSIVE STATUS CHECK")
    print("=" * 70)
    
    issues = []
    successes = []
    
    # Check 1: Core Module Imports
    print("\n📦 CHECKING CORE MODULES:")
    try:
        from src.models import EthicalStance, DilemmaCategory, ModelResponse
        from src.database import EthicsDatabase, DilemmaLoader
        from src.testing import EthicsTestRunner, MockAIModel
        successes.append("✅ All core modules import successfully")
    except Exception as e:
        issues.append(f"❌ Core module import failed: {e}")
    
    # Check 2: Database Functionality  
    print("\n🗄️ CHECKING DATABASE:")
    try:
        db = EthicsDatabase("status_check.db")
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM responses")
            count = cursor.fetchone()[0]
        successes.append(f"✅ Database connection works (found {count} responses)")
        
        # Clean up test database
        os.unlink("status_check.db")
        if os.path.exists("status_check.db-wal"):
            os.unlink("status_check.db-wal")
        if os.path.exists("status_check.db-shm"):
            os.unlink("status_check.db-shm")
            
    except Exception as e:
        issues.append(f"❌ Database test failed: {e}")
    
    # Check 3: Dilemma Loading
    print("\n📚 CHECKING ETHICAL DILEMMAS:")
    try:
        dilemmas = DilemmaLoader.load_dilemmas("ethical_dilemmas.json")
        if len(dilemmas) >= 50:
            successes.append(f"✅ Successfully loaded {len(dilemmas)} ethical dilemmas")
        else:
            issues.append(f"⚠️ Only {len(dilemmas)} dilemmas loaded (expected 50+)")
    except Exception as e:
        issues.append(f"❌ Dilemma loading failed: {e}")
    
    # Check 4: Template Files
    print("\n🌐 CHECKING WEB TEMPLATES:")
    templates = ['dashboard.html', 'vue_dashboard.html', 'advanced_dashboard.html']
    for template in templates:
        template_path = Path("templates") / template
        if template_path.exists():
            successes.append(f"✅ Template {template} exists")
        else:
            issues.append(f"❌ Template {template} missing")
    
    # Check 5: Web App Compilation
    print("\n🚀 CHECKING WEB APPLICATION:")
    try:
        import py_compile
        py_compile.compile("src/web_app.py", doraise=True)
        successes.append("✅ Web application compiles without syntax errors")
    except Exception as e:
        issues.append(f"❌ Web app compilation failed: {e}")
    
    # Check 6: Demo Functionality
    print("\n🧪 CHECKING DEMO FUNCTIONALITY:")
    try:
        # Simple test without running full demo
        runner = EthicsTestRunner()
        model = MockAIModel("test-model")
        successes.append("✅ Test runner and mock model creation works")
    except Exception as e:
        issues.append(f"❌ Demo functionality test failed: {e}")
    
    # Check 7: Flask Availability
    print("\n🌐 CHECKING FLASK AVAILABILITY:")
    try:
        import flask
        successes.append(f"✅ Flask available (version {flask.__version__})")
    except ImportError:
        issues.append("⚠️ Flask not installed - web interface unavailable")
        issues.append("💡 Run: pip install flask flask-cors")
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 SUMMARY:")
    print(f"✅ Successes: {len(successes)}")
    print(f"❌ Issues: {len(issues)}")
    
    if successes:
        print("\n🎉 WORKING FEATURES:")
        for success in successes:
            print(f"   {success}")
    
    if issues:
        print("\n🚨 ISSUES TO ADDRESS:")
        for issue in issues:
            print(f"   {issue}")
    else:
        print("\n🎉 ALL SYSTEMS OPERATIONAL!")
    
    # Critical Issues vs Minor Issues
    critical_issues = [i for i in issues if "❌" in i]
    minor_issues = [i for i in issues if "⚠️" in i]
    
    print(f"\n🔥 Critical Issues: {len(critical_issues)}")
    print(f"⚠️ Minor Issues: {len(minor_issues)}")
    
    if len(critical_issues) == 0:
        print("\n🚀 SYSTEM STATUS: FULLY OPERATIONAL")
        print("💡 The AI Ethics Testing Framework is ready for use!")
        return True
    else:
        print("\n⚠️ SYSTEM STATUS: NEEDS ATTENTION")
        print("💡 Address critical issues before using in production")
        return False

if __name__ == "__main__":
    success = check_system_status()
    sys.exit(0 if success else 1)
