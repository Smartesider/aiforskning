#!/usr/bin/env python3
"""
Simple database test for AI Ethics Testing Framework
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    print("Testing database connection...")
    # 🧷 Kun MariaDB skal brukes – ingen andre drivere!
    from src.database import database
    print("✅ Database import successful")
    
    # Test database connection
    with database.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        result = cursor.fetchone()
        print(f"✅ Database connection successful: {result}")
    
    print("✅ All database tests passed!")
    
except Exception as e:
    print(f"❌ Database test failed: {e}")
    import traceback
    traceback.print_exc()
