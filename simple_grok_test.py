#!/usr/bin/env python3
"""
Simple test for xAI API key validation
"""

import pymysql
import requests
import json

def test_grok_simple():
    """Simple test for xAI Grok"""
    try:
        # Get API key from database
        db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'skyforskning',
            'passwd': 'Klokken!12!?!',
            'db': 'skyforskning',
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key_value FROM api_keys WHERE provider = 'xAI'")
        result = cursor.fetchone()
        
        if result:
            api_key = result[0]
            print(f"✅ Found xAI API key (length: {len(api_key)})")
            
            # Test with simple request
            url = "https://api.x.ai/v1/models"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            print("🚀 Testing xAI API connection...")
            
            try:
                response = requests.get(url, headers=headers, timeout=10)
                print(f"Status code: {response.status_code}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ API connection successful!")
                    print(f"Available models: {len(data.get('data', []))}")
                    return True
                else:
                    print(f"❌ API connection failed: {response.text}")
                    return False
            except Exception as e:
                print(f"❌ Connection error: {e}")
                return False
        else:
            print("❌ No xAI API key found")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = test_grok_simple()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)
