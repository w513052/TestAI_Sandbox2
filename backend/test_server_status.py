#!/usr/bin/env python3
"""
Test if the server is running and what's causing the 500 error.
"""

import requests

def test_server_status():
    """Test server status."""
    
    print("🔍 Testing Server Status")
    print("=" * 30)
    
    try:
        # Test basic endpoint
        response = requests.get('http://127.0.0.1:8000/api/v1/audits', timeout=5)
        print(f"Audits endpoint: {response.status_code}")
        
        if response.status_code == 200:
            audits = response.json()['data']
            print(f"Found {len(audits)} audits")
            
            # Test analysis endpoint with a specific audit
            if audits:
                audit_id = audits[0]['audit_id']
                print(f"\nTesting analysis endpoint with audit {audit_id}...")
                
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis', timeout=10)
                print(f"Analysis endpoint: {analysis_response.status_code}")
                
                if analysis_response.status_code != 200:
                    print(f"Error response: {analysis_response.text}")
                else:
                    print(f"Analysis working!")
            
        return response.status_code == 200
        
    except requests.exceptions.ConnectionError:
        print("❌ Server not running")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_server_status()
