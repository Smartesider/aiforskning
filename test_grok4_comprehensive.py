#!/usr/bin/env python3
"""
Test Grok-4 specifically with correct model name
Following AI enforcement rules
"""

import pymysql
import requests
import json
import time

def test_grok4():
    """Test Grok-4 model specifically"""
    
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
        print("🔍 Testing Grok-4 model...")
        
        # Get API key from MariaDB
        conn = pymysql.connect(**db_config)
        cursor = conn.cursor()
        
        cursor.execute("SELECT key_value FROM api_keys WHERE provider = 'xAI' AND status = 'active'")
        result = cursor.fetchone()
        
        if not result:
            print("❌ No active xAI API key found")
            return False
        
        api_key = result[0]
        print(f"✅ Found xAI API key (length: {len(api_key)})")
        
        # Test Grok-4 with correct model name
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Test question for bias detection
        test_question = "What are the key principles of ethical AI development?"
        
        payload = {
            "model": "grok-4-0709",  # Correct Grok-4 model name
            "messages": [{"role": "user", "content": test_question}],
            "max_tokens": 200,
            "temperature": 0.7
        }
        
        print(f"🚀 Testing Grok-4 (model: grok-4-0709)...")
        print(f"📝 Question: {test_question}")
        
        start_time = time.time()
        response = requests.post(url, headers=headers, json=payload, timeout=30)
        response_time = int((time.time() - start_time) * 1000)
        
        print(f"⏱️  Response time: {response_time}ms")
        print(f"📊 HTTP Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            content = data['choices'][0]['message']['content']
            
            print(f"✅ Grok-4 test SUCCESSFUL!")
            print(f"🧠 Model: {data.get('model', 'grok-4-0709')}")
            print(f"📝 Response preview: {content[:200]}...")
            
            # Update database with successful test
            cursor.execute("""
                UPDATE api_keys 
                SET status = 'active', last_tested = NOW(), response_time = %s,
                    name = 'Grok-4 (0709)'
                WHERE provider = 'xAI'
            """, (response_time,))
            
            print(f"💾 Database updated with test results")
            return True
            
        else:
            error_text = response.text
            print(f"❌ Grok-4 test FAILED: HTTP {response.status_code}")
            print(f"🚨 Error: {error_text}")
            
            # Update database with error status
            cursor.execute("""
                UPDATE api_keys 
                SET status = 'error', last_tested = NOW()
                WHERE provider = 'xAI'
            """)
            
            return False
            
    except Exception as e:
        print(f"❌ Exception during Grok-4 test: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

def test_via_api():
    """Test Grok-4 via our FastAPI endpoint"""
    
    print("\n🔗 Testing via FastAPI endpoint...")
    
    # Read port from required file
    with open('/home/skyforskning.no/port.txt', 'r') as f:
        port = f.read().strip()
    
    # 🧷 Dette skal være en fetch til FastAPI på portnummer du finner under home/{domene}/port.txt, som svarer med JSON
    url = f"http://localhost:{port}/api/v1/available-models"
    
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            xai_models = data.get('models', {}).get('xAI', [])
            print(f"✅ Available xAI models: {xai_models}")
            
            if 'grok-4-0709' in xai_models:
                print(f"🎯 Grok-4 model correctly configured!")
                return True
            else:
                print(f"⚠️  Grok-4 model not found in available models")
                return False
        else:
            print(f"❌ API call failed: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧠 GROK-4 COMPREHENSIVE TEST")
    print("="*50)
    
    # Test direct API
    direct_success = test_grok4()
    
    # Test via FastAPI
    api_success = test_via_api()
    
    print("\n" + "="*50)
    print("📊 FINAL RESULTS:")
    print(f"🔌 Direct xAI API: {'✅ SUCCESS' if direct_success else '❌ FAILED'}")
    print(f"🌐 FastAPI Integration: {'✅ SUCCESS' if api_success else '❌ FAILED'}")
    
    overall_success = direct_success and api_success
    print(f"🎯 Overall Status: {'✅ GROK-4 FULLY OPERATIONAL' if overall_success else '❌ ISSUES DETECTED'}")
    
    exit(0 if overall_success else 1)
