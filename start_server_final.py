#!/usr/bin/env python3
# 🧷 Kun MariaDB skal brukes – ingen andre drivere!

import os
import sys

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from src.web_app import create_app
    
    # Get port from file according to AI enforcement rules
    # ❌ Ikke gjett – les fra den filen!
    with open('/home/skyforskning.no/port.txt', 'r') as f:
        port = int(f.read().strip())
    
    print(f"🚀 Starting AI Ethics Testing Framework server on port {port}")
    print("📊 Admin panel available at /admin/")
    print("👤 User dashboard available at /bruker/")
    print("🧷 Backend skal KUN kjøre på porten spesifisert i /home/skyforskning.no/port.txt")
    
    app = create_app()
    app.run(host='0.0.0.0', port=port, debug=True)
    
except Exception as e:
    print(f"❌ Failed to start server: {e}")
    sys.exit(1)
