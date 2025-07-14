#!/usr/bin/env python3
"""
Test if the server is running.
"""

import socket

def test_server():
    """Test if server is running on port 8000."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 8000))
        sock.close()
        
        if result == 0:
            print("✅ Server is running on http://127.0.0.1:8000")
            print("🌐 API documentation: http://127.0.0.1:8000/docs")
            print("📊 API endpoints: http://127.0.0.1:8000/api/v1/audits")
            return True
        else:
            print("❌ Server is not running on port 8000")
            return False
    except Exception as e:
        print(f"❌ Error testing server: {e}")
        return False

if __name__ == "__main__":
    test_server()
