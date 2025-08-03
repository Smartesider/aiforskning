#!/usr/bin/env python3
"""
Startup script for FastAPI backend
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import uvicorn
    from src.fastapi_app import app
    
    if __name__ == "__main__":
        print("Starting FastAPI server on port 8010...")
        uvicorn.run(app, host="0.0.0.0", port=8010, log_level="info")
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Please install dependencies: pip install fastapi uvicorn")
    sys.exit(1)
except Exception as e:
    print(f"Error starting server: {e}")
    sys.exit(1)
