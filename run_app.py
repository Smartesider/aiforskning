#!/usr/bin/env python3
"""
Production-ready runner for the AI Ethics Testing Framework web application
"""

import os
import sys
from pathlib import Path

# Add src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Import Flask app for gunicorn
from src.web_app import create_app

# Create the Flask app instance for gunicorn
app = create_app()

def main():
    """Run the web application with proper error handling"""
    try:
        from src.web_app import create_app
        
        # Create the Flask app
        app = create_app()
        
        # Configuration
        host = os.environ.get('HOST', '0.0.0.0')
        port = int(os.environ.get('PORT', 8010))
        debug = os.environ.get('DEBUG', 'False').lower() == 'true'
        
        print(f"🚀 Starting AI Ethics Testing Framework")
        print(f"📍 Server: http://{host}:{port}")
        print(f"🔧 Debug mode: {debug}")
        print(f"📂 Working directory: {Path.cwd()}")
        
        # Run the application
        app.run(
            host=host,
            port=port,
            debug=debug,
            threaded=True,  # Enable threading for better concurrency
            use_reloader=False  # Disable reloader to prevent issues
        )
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Make sure all required dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Application startup failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
