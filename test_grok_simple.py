#!/usr/bin/env python3
"""
Simple Grok API test to debug the hanging issue
"""

import asyncio
import aiohttp
import pymysql
import sys

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 3306,
    'user': 'skyforskning',
    'passwd': 'Klokken!12!?!',
    'db': 'skyforskning',
    'charset': 'utf8mb4',
    'autocommit': True
}

async def test_grok_simple():
    """Simple test of Grok API"""
    print("Starting simple Grok test...")
    
    # Get API key from database
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT key_value FROM api_keys WHERE provider = 'xAI' AND status IN ('active', 'error')")
        result = cursor.fetchone()
        if not result:
            print("❌ No xAI API key found")
            return False
        api_key = result[0]
        print("✅ API key retrieved")
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False
    
    # Test API request
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messages": [
            {
                "role": "user", 
                "content": "What are your thoughts on government regulation of free markets?"
            }
        ],
        "model": "grok-2-1212",
        "temperature": 0.7,
        "max_tokens": 500
    }
    
    try:
        print("Creating aiohttp session...")
        timeout = aiohttp.ClientTimeout(total=30)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            print("Making API request...")
            async with session.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=payload
            ) as response:
                print(f"Response status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    content = result['choices'][0]['message']['content']
                    print(f"✅ Success! Response length: {len(content)}")
                    print(f"First 200 chars: {content[:200]}...")
                    return True
                else:
                    error_text = await response.text()
                    print(f"❌ API error {response.status}: {error_text}")
                    return False
    except asyncio.TimeoutError:
        print("❌ Request timed out")
        return False
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_grok_simple())
    sys.exit(0 if result else 1)
