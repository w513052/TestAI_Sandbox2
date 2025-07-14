#!/usr/bin/env python3
"""
Simple script to start the FastAPI server.
"""

import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("Python version:", sys.version)
print("Current directory:", os.getcwd())
print("Python path:", sys.path[:3])

try:
    print("Importing uvicorn...")
    import uvicorn
    print("✓ uvicorn imported successfully")

    print("Importing FastAPI app...")
    from src.main import app
    print("✓ FastAPI app imported successfully")

    print("Starting FastAPI server...")
    print("Server will be available at: http://127.0.0.1:8000")
    print("API documentation at: http://127.0.0.1:8000/docs")
    print("Press Ctrl+C to stop the server")

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False,  # Disable reload to avoid issues
        log_level="info"
    )
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Please make sure all dependencies are installed")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error starting server: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
