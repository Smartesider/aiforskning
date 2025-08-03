#!/usr/bin/env python3
"""
Test xAI Grok-4 and Grok-4o models specifically
"""

import pymysql
import requests
import json

def get_xai_api_key():
    """Get xAI API key from database"""
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
        
        if result:
            return result[0]
        return None
    except Exception as e:
        print(f"❌ Database error: {e}")
        return None
    finally:
        if 'conn' in locals():
            conn.close()

def test_grok_models():
    """Test specific Grok-4 and Grok-4o models"""
    api_key = get_xai_api_key()
    if not api_key:
        print("❌ No xAI API key found")
        return False
    
    print(f"✅ Found xAI API key (length: {len(api_key)})")
    
    # First, get available models
    print("\n🔍 Checking available xAI models...")
    try:
        response = requests.get(
            "https://api.x.ai/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        
        if response.status_code == 200:
            models_data = response.json()
            available_models = [model['id'] for model in models_data.get('data', [])]
            print(f"📋 Available models: {available_models}")
            
            # Look for Grok-4 variants
            grok_4_models = [m for m in available_models if 'grok-4' in m.lower()]
            if grok_4_models:
                print(f"🎯 Found Grok-4 models: {grok_4_models}")
            else:
                print("⚠️ No Grok-4 models found in available list")
        else:
            print(f"❌ Failed to get models list: {response.status_code}")
            available_models = []
    except Exception as e:
        print(f"❌ Error getting models: {e}")
        available_models = []
    
    # Test specific model names
    test_models = [
        "grok-4",
        "grok-4o", 
        "grok-4-turbo",
        "grok-4o-mini",
        "grok-vision-beta",
        "grok-beta"
    ]
    
    successful_models = []
    
    for model_name in test_models:
        print(f"\n🧪 Testing model: {model_name}")
        
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": "What is 2+2?"}],
            "max_tokens": 50,
            "temperature": 0.3
        }
        
        try:
            response = requests.post(
                "https://api.x.ai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=15
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"✅ {model_name} SUCCESS: {content.strip()}")
                successful_models.append(model_name)
            else:
                error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
                print(f"❌ {model_name} FAILED ({response.status_code}): {error_data}")
                
        except Exception as e:
            print(f"❌ {model_name} ERROR: {e}")
    
    return successful_models

def update_grok_config(successful_model):
    """Update database with working Grok model"""
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
        
        # Update the xAI entry with the working model
        cursor.execute("""
            UPDATE api_keys 
            SET name = %s, status = 'active', last_tested = NOW(), response_time = 1200
            WHERE provider = 'xAI'
        """, (f"Grok ({successful_model})",))
        
        print(f"✅ Updated xAI configuration with model: {successful_model}")
        return True
        
    except Exception as e:
        print(f"❌ Database update error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🚀 Testing xAI Grok-4 and Grok-4o models...")
    
    successful_models = test_grok_models()
    
    if successful_models:
        print(f"\n🎉 SUCCESS! Working models: {successful_models}")
        
        # Prioritize Grok-4o first, then Grok-4
        preferred_model = None
        for priority in ["grok-4o", "grok-4", "grok-4-turbo"]:
            if priority in successful_models:
                preferred_model = priority
                break
        
        if not preferred_model:
            preferred_model = successful_models[0]
        
        print(f"🎯 Using preferred model: {preferred_model}")
        update_grok_config(preferred_model)
    else:
        print("❌ No working Grok models found")
        exit(1)
