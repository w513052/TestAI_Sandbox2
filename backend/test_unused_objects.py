import requests
import json

def test_unused_objects():
    """Test the unused objects counting with sample-obj.xml (20 objects, 0 rules)."""
    url = "http://127.0.0.1:8000/api/v1/audits/"
    
    # Prepare the file and form data
    with open("test_usage_config.xml", "rb") as f:
        files = {"file": ("test_usage_config.xml", f, "application/xml")}
        data = {"session_name": "Test 20 Unused Objects"}
        
        try:
            response = requests.post(url, files=files, data=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("\n✅ Unused objects test successful!")
                result = response.json()
                metadata = result['data']['metadata']
                print(f"\n📊 Parsed Results:")
                print(f"   Rules: {metadata.get('rules_parsed', 0)}")
                print(f"   Objects: {metadata.get('objects_parsed', 0)}")
                print(f"\n🎯 This should show '0 used, 20 unused objects' in the logs!")
                return response.json()
            else:
                print(f"\n❌ Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

if __name__ == "__main__":
    test_unused_objects()
