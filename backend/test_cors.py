import requests

def test_cors():
    """Test CORS headers from the frontend's perspective."""
    
    print("🧪 Testing CORS Configuration")
    print("=" * 40)
    
    # Test health endpoint with CORS headers
    headers = {
        'Origin': 'http://localhost:5175',
        'Access-Control-Request-Method': 'GET',
        'Access-Control-Request-Headers': 'Content-Type'
    }
    
    try:
        # Test preflight request (OPTIONS)
        print("\n1️⃣ Testing preflight request (OPTIONS)")
        options_response = requests.options('http://127.0.0.1:8000/health', headers=headers)
        print(f"   Status: {options_response.status_code}")
        print(f"   CORS Headers:")
        for header, value in options_response.headers.items():
            if 'access-control' in header.lower():
                print(f"      {header}: {value}")
        
        # Test actual request (GET)
        print("\n2️⃣ Testing actual request (GET)")
        get_response = requests.get('http://127.0.0.1:8000/health', headers={'Origin': 'http://localhost:5175'})
        print(f"   Status: {get_response.status_code}")
        print(f"   Response: {get_response.json()}")
        print(f"   CORS Headers:")
        for header, value in get_response.headers.items():
            if 'access-control' in header.lower():
                print(f"      {header}: {value}")
        
        # Check if CORS is properly configured
        cors_origin = get_response.headers.get('access-control-allow-origin')
        if cors_origin:
            if cors_origin == 'http://localhost:5175' or cors_origin == '*':
                print(f"\n✅ CORS is properly configured!")
                print(f"   Frontend (http://localhost:5175) can access backend")
                return True
            else:
                print(f"\n❌ CORS origin mismatch: {cors_origin}")
                return False
        else:
            print(f"\n❌ No CORS headers found")
            return False
            
    except Exception as e:
        print(f"❌ CORS test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_cors()
    if success:
        print(f"\n🚀 Frontend should now be able to connect to backend!")
        print(f"   Refresh the browser page at http://localhost:5175")
    else:
        print(f"\n💥 CORS configuration needs fixing")
