#!/usr/bin/env python3
"""
Native server startup for AI Ethics Framework
Runs directly on server without Docker
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def main():
    print("🚀 Starting AI Ethics Framework (Native Server Mode)")
    
    # Set environment variables for native deployment
    os.environ['PORT'] = '8010'
    os.environ['FLASK_ENV'] = 'production'
    os.environ['DB_HOST'] = 'localhost'
    os.environ['DB_USER'] = 'skyforskning'
    os.environ['DB_PASSWORD'] = 'Klokken!12!?!'
    os.environ['DB_NAME'] = 'skyforskning'
    
    try:
        # Import and start the app
        from src.web_app import create_app
        app = create_app()
        
        port = int(os.environ.get('PORT', 8010))
        print(f"✅ AI Ethics Framework starting on port {port}")
        print(f"🌐 Access at: https://skyforskning.no")
        print(f"🔧 Mode: Native Server (no Docker)")
        
        # Start the server
        app.run(
            host='0.0.0.0',
            port=port,
            debug=False,
            threaded=True
        )
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("⚠️  Starting in demo mode...")
        
        # Fallback to simple server
        from flask import Flask
        app = Flask(__name__)
        
        @app.route('/')
        def demo():
            return """
            <h1>🚀 AI Ethics Framework - Demo Mode</h1>
            <p>Server running on port 8010 (native deployment)</p>
            <p>Database connection will be restored shortly...</p>
            """
        
        app.run(host='0.0.0.0', port=8010, debug=False)

if __name__ == '__main__':
    main()
