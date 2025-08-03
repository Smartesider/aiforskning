#!/usr/bin/env python3
"""
Test xAI Grok API specifically
"""

import asyncio
import aiohttp
import pymysql
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_grok():
    """Test xAI Grok API directly"""
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
        
        if not result:
            logger.error("❌ No xAI API key found")
            return False
        
        api_key = result[0]
        logger.info(f"✅ Found xAI API key (length: {len(api_key)})")
        
        # Test xAI API
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "grok-beta",
            "messages": [{"role": "user", "content": "What is artificial intelligence?"}],
            "max_tokens": 100,
            "temperature": 0.7
        }
        
        logger.info("🚀 Testing xAI Grok API...")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload, timeout=30) as response:
                logger.info(f"Response status: {response.status}")
                
                if response.status == 200:
                    data = await response.json()
                    content = data['choices'][0]['message']['content']
                    logger.info(f"✅ Grok test successful!")
                    logger.info(f"Response: {content[:200]}...")
                    
                    # Update database status
                    cursor.execute("""
                        UPDATE api_keys 
                        SET status = 'active', last_tested = NOW(), response_time = 1000 
                        WHERE provider = 'xAI'
                    """)
                    
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"❌ Grok test failed: HTTP {response.status}")
                    logger.error(f"Error: {error_text}")
                    
                    # Update database status
                    cursor.execute("""
                        UPDATE api_keys 
                        SET status = 'error', last_tested = NOW() 
                        WHERE provider = 'xAI'
                    """)
                    
                    return False
                    
    except Exception as e:
        logger.error(f"❌ Exception during Grok test: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = asyncio.run(test_grok())
    print(f"\n{'✅ SUCCESS' if success else '❌ FAILED'}: xAI Grok test")
    exit(0 if success else 1)
