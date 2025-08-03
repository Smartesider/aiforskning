#!/usr/bin/env python3
"""
Test script for the AI Ethics Testing Framework
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.web_app import create_app

if __name__ == '__main__':
    app = create_app()
    print("🚀 Starting AI Ethics Testing Framework on port 8010...")
    print("🧷 Kun MariaDB skal brukes – ingen andre drivere!")
    print("🛑 Ingen templating! HTML-servering skjer via statiske filer – kun API med JSON")
    try:
        app.run(host='0.0.0.0', port=8010, debug=False)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
