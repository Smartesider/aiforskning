#!/usr/bin/env python3
"""
Startup script for AI Ethics Testing Framework
Fixes relative import issues and starts the Flask server
"""

import sys
import os
sys.path.insert(0, '/home/skyforskning.no/forskning')

# Now import and run the web app
from src.web_app import create_app

if __name__ == '__main__':
    app = create_app()
    port = 8010
    print(f"🧷 Starting AI Ethics Testing Framework on port {port}")
    print(f"🧷 Admin panel available at: http://localhost:{port}/admin/")
    print(f"🧷 User dashboard available at: http://localhost:{port}/bruker/")
    print(f"🧷 API documentation available at: http://localhost:{port}/api/health")
    app.run(host='0.0.0.0', port=port, debug=False)
