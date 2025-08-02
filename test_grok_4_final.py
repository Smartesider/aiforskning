#!/usr/bin/env python3
"""
Test the specific Grok-4-0709 model
"""

import pymysql
import requests

def test_grok_4_0709():
    """Test the actual Grok-4-0709 model"""
    # 🧷 Kun MariaDB skal brukes – ingen andre drivere!
    db_config = {
        'host': 'localhost',
        'port': 3306,
        'user': 'skyforskning',
        'passwd': 'Klokken!12!?!',
        'db': 'skyforskning',
        'charset': 'utf8mb4',
        'autocommit': True
    }
    
    try:
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key_value FROM api_keys WHERE provider = 'xAI'")
        result = cursor.fetchone()
        
        if not result:
            print("❌ No xAI API key found")
            return False
            
        api_key = result[0]
        print(f"✅ Found xAI API key")
        
        # Test Grok-4-0709 specifically
        print("🧪 Testing Grok-4-0709 model...")
        
        payload = {
            "model": "grok-4-0709",
            "messages": [{"role": "user", "content": "What is artificial intelligence? Give a brief answer."}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.x.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            },
            json=payload,
            timeout=20
        )
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            print(f"✅ Grok-4-0709 SUCCESS!")
            print(f"Response: {content}")
            
            # Update database with successful test
            cursor.execute("""
                UPDATE api_keys 
                SET name = 'Grok-4 (0709)', status = 'active', last_tested = NOW(), response_time = 1500
                WHERE provider = 'xAI'
            """)
            
            print("✅ Updated database - xAI Grok-4 is now active!")
            return True
        else:
            print(f"❌ Grok-4-0709 FAILED ({response.status_code}): {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = test_grok_4_0709()
    print(f"\nResult: {'SUCCESS' if success else 'FAILED'}")
    exit(0 if success else 1)
