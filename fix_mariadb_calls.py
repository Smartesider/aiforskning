#!/usr/bin/env python3
"""
Quick fix script to convert SQLite-style conn.execute() to MariaDB-style cursor.execute()
"""

import re

def fix_database_calls():
    with open('/home/skyforskning.no/forskning/src/web_app.py', 'r') as f:
        content = f.read()
    
    # Pattern 1: cursor = conn.execute(
    content = re.sub(
        r'cursor = conn\.execute\(',
        'cursor = conn.cursor()\n            cursor.execute(',
        content
    )
    
    # Pattern 2: standalone conn.execute(
    content = re.sub(
        r'(\s+)conn\.execute\(',
        r'\1cursor = conn.cursor()\n\1cursor.execute(',
        content
    )
    
    # Fix row access from ['column'] to [index] for some cases
    # This is more complex and may need manual review
    
    with open('/home/skyforskning.no/forskning/src/web_app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed database connection calls for MariaDB compatibility")

if __name__ == '__main__':
    fix_database_calls()
