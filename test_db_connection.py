#!/usr/bin/env python3
import MySQLdb

try:
    conn = MySQLdb.connect(host='localhost', user='skyforskning', passwd='Klokken!12!?!', db='skyforskning')
    print('✅ Database connection successful!')
    conn.close()
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    # Try without specifying database
    try:
        conn = MySQLdb.connect(host='localhost', user='skyforskning', passwd='Klokken!12!?!')
        print('✅ User connection successful (no database specified)')
        conn.close()
    except Exception as e2:
        print(f'❌ User connection also failed: {e2}')
