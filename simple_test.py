#!/usr/bin/env python3
"""
Simple database and API test
"""

import pymysql as MySQLdb
import requests
import json

def test_database():
    """Test database connection"""
    try:
        db_config = {
            'host': 'localhost',
            'port': 3306,
            'user': 'skyforskning',
            'passwd': 'Klokken!12!?!',
            'db': 'skyforskning',
            'charset': 'utf8mb4',
            'autocommit': True
        }
        
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()
        
        print("✓ Database connection successful")
        
        # Get API keys
        cursor.execute("SELECT provider, status FROM api_keys WHERE status = 'active'")
        results = cursor.fetchall()
        
        print(f"✓ Found {len(results)} active API keys:")
        for provider, status in results:
            print(f"  - {provider}: {status}")
        
        # Get one OpenAI key for testing
        cursor.execute("SELECT key_value FROM api_keys WHERE provider = 'OpenAI' AND status = 'active' LIMIT 1")
        result = cursor.fetchone()
        
        if result:
            api_key = result[0]
            print(f"✓ Retrieved OpenAI key: {api_key[:10]}...")
            
            # Test API call with requests (simpler)
            try:
                url = "https://api.openai.com/v1/chat/completions"
                headers = {
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-3.5-turbo",  # Use cheaper model for testing
                    "messages": [{"role": "user", "content": "Say 'API test successful'"}],
                    "max_tokens": 10
                }
                
                print("🔄 Testing OpenAI API...")
                response = requests.post(url, headers=headers, json=payload, timeout=30)
                
                if response.status_code == 200:
                    data = response.json()
                    answer = data['choices'][0]['message']['content']
                    print(f"✅ OpenAI API test successful: {answer.strip()}")
                    return True
                else:
                    print(f"❌ OpenAI API test failed: {response.status_code} - {response.text}")
                    return False
                    
            except Exception as e:
                print(f"❌ API test error: {e}")
                return False
        else:
            print("❌ No OpenAI API key found")
            return False
            
        conn.close()
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running simple API test...")
    success = test_database()
    if success:
        print("🎉 Test completed successfully!")
    else:
        print("💥 Test failed!")
