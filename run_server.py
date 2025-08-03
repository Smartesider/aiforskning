#!/usr/bin/env python3
"""
AI Ethics Framework - Flask Application Launcher
Following project lock restrictions - Port 8010 only
"""

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.web_app import create_app

if __name__ == '__main__':
    app = create_app()
    
    # 🔐 Port 8010 as specified in .project.lock
    PORT = 8010
    
    print(f"🚀 Starting AI Ethics Framework on port {PORT}")
    print(f"📊 Admin panel: http://localhost:{PORT}/admin/")
    print(f"🔍 API health: http://localhost:{PORT}/api/health")
    print("🧷 Following project lock restrictions - all changes remain inside project")
    
    # Run with debug=False for production, on specified port
    app.run(host='0.0.0.0', port=PORT, debug=False)
