#!/usr/bin/env python3
"""
Quick API test to verify real LLM connections
"""

import asyncio
import aiohttp
import pymysql as MySQLdb
import json
from datetime import datetime

async def test_single_api():
    """Test a single API to verify connections work"""
    
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
    
    try:
        conn = MySQLdb.connect(**db_config)
        cursor = conn.cursor()
        cursor.execute("SELECT key_value FROM api_keys WHERE provider = 'OpenAI' AND status = 'active'")
        result = cursor.fetchone()
        
        if not result:
            print("No OpenAI API key found")
            return
        
        api_key = result[0]
        print(f"Found OpenAI API key: {api_key[:10]}...")
        
        # Test OpenAI API
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-4",
            "messages": [{"role": "user", "content": "What is 2+2? Answer briefly."}],
            "max_tokens": 50
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as response:
                if response.status == 200:
                    data = await response.json()
                    answer = data['choices'][0]['message']['content']
                    print(f"✓ OpenAI API test successful: {answer.strip()}")
                    
                    # Save to database
                    cursor.execute("""
                        INSERT INTO responses (
                            prompt_id, model, timestamp, response_text, 
                            sentiment_score, stance, certainty_score, 
                            keywords, response_length, session_id
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        "test_1",
                        "gpt-4",
                        datetime.now(),
                        answer.strip(),
                        0.5,  # neutral sentiment
                        "neutral",
                        0.8,
                        "[]",
                        len(answer),
                        f"quick_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                    ))
                    
                    print("✓ Result saved to database")
                    
                else:
                    error_text = await response.text()
                    print(f"✗ OpenAI API test failed: HTTP {response.status} - {error_text}")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_single_api())
