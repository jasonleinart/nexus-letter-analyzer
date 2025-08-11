#!/usr/bin/env python3
"""
Startup script for the Nexus Letter Analysis API.
"""

import os
import sys
import subprocess

def main():
    """Start the FastAPI server."""
    # Add src to path
    src_path = os.path.join(os.path.dirname(__file__), 'src')
    sys.path.insert(0, src_path)
    
    # Change to src directory
    os.chdir(src_path)
    
    print("🚀 Starting Nexus Letter Analysis API...")
    print("📊 Streamlit dashboard: http://localhost:8502")
    print("🔧 FastAPI server: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("📋 Interactive API: http://localhost:8000/redoc")
    print("\n" + "=" * 60)
    
    try:
        # Start the API server
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "api.main:app", 
            "--host", "0.0.0.0",
            "--port", "8000", 
            "--reload",
            "--log-level", "info"
        ])
    except KeyboardInterrupt:
        print("\n🛑 API server stopped")

if __name__ == "__main__":
    main()