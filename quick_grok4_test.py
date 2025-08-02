#!/usr/bin/env python3
"""
Quick Grok-4 validation test
"""

import pymysql
import requests
import json

def quick_grok4_test():
    """Quick test to confirm Grok-4 is accessible"""
    
    # 🧷 Kun MariaDB skal brukes – ingen andre drivere!
    try:
        conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='skyforskning',
            passwd='Klokken!12!?!',
            db='skyforskning',
            charset='utf8mb4',
            autocommit=True
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT key_value FROM api_keys WHERE provider = 'xAI'")
        result = cursor.fetchone()
        
        if result:
            api_key = result[0]
            print(f"✅ API Key found (length: {len(api_key)})")
            
            # Test models endpoint first (faster)
            headers = {"Authorization": f"Bearer {api_key}"}
            response = requests.get("https://api.x.ai/v1/models", headers=headers, timeout=10)
            
            if response.status_code == 200:
                models = response.json()
                model_names = [model['id'] for model in models.get('data', [])]
                print(f"✅ API Connection successful")
                print(f"📋 Available models: {model_names}")
                
                # Check if Grok-4 models are available
                grok4_models = [m for m in model_names if 'grok-4' in m.lower()]
                if grok4_models:
                    print(f"🎯 Grok-4 models found: {grok4_models}")
                    return True, grok4_models[0]  # Return first Grok-4 model
                else:
                    print(f"⚠️  No Grok-4 models found")
                    return False, None
            else:
                print(f"❌ API call failed: {response.status_code}")
                return False, None
        else:
            print("❌ No API key found")
            return False, None
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("🔍 Quick Grok-4 Validation Test")
    success, model_name = quick_grok4_test()
    
    if success:
        print(f"✅ GROK-4 IS READY! Model: {model_name}")
    else:
        print("❌ Grok-4 validation failed")
    
    exit(0 if success else 1)
