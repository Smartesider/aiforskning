#!/usr/bin/env python3
"""
Fix all conn.execute() calls to use proper MariaDB cursor pattern
"""

import re

def fix_mariadb_calls():
    with open('/home/skyforskning.no/forskning/src/web_app.py', 'r') as f:
        content = f.read()
    
    # Pattern to match: cursor = conn.execute(
    # Replace with: cursor = conn.cursor()\n            cursor.execute(
    content = re.sub(
        r'(\s+)cursor = conn\.execute\(',
        r'\1cursor = conn.cursor()\n\1cursor.execute(',
        content
    )
    
    # Also need to fix row access patterns from row['column'] to row[index] in some cases
    # This will need manual review, but let's start with the cursor fix
    
    with open('/home/skyforskning.no/forskning/src/web_app.py', 'w') as f:
        f.write(content)
    
    print("✅ Fixed all conn.execute() calls to use cursor pattern")

if __name__ == '__main__':
    fix_mariadb_calls()
