#!/usr/bin/env python3
"""
Production server for AI Ethics Testing Framework
Configured to accept connections from skyforskning.no domain
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # Read port from configuration file
    # 🧷 Backend skal KUN kjøre på porten spesifisert i /home/{domenenavn}/port.txt
    port_file = '/home/skyforskning.no/port.txt'
    try:
        with open(port_file, 'r') as f:
            port = int(f.read().strip())
        print(f"✅ Using port {port} from {port_file}")
    except Exception as e:
        print(f"⚠️  Could not read port from {port_file}: {e}")
        port = 8010
        print(f"🔄 Falling back to default port {port}")
    
    print(f"🚀 Starting AI Ethics Testing Framework on port {port}...")
    print("🌐 Accepting connections from skyforskning.no and localhost")
    print("🧷 Kun MariaDB skal brukes – ingen andre drivere!")
    print("🛑 Ingen templating! HTML-servering skjer via statiske filer – kun API med JSON")
    
    try:
        # Accept connections from all interfaces (including domain)
        app.run(
            host='0.0.0.0', 
            port=port, 
            debug=False,
            threaded=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
