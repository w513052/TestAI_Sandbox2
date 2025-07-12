import requests
import json

def test_set_format_upload():
    """Test the file upload endpoint with our sample set-format config."""
    url = "http://127.0.0.1:8000/api/v1/audits/"
    
    # Prepare the file and form data
    with open("test_set_config.txt", "rb") as f:
        files = {"file": ("test_set_config.txt", f, "text/plain")}
        data = {"session_name": "Set Format Test Session"}
        
        try:
            response = requests.post(url, files=files, data=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("\n✅ Set format file upload and parsing successful!")
                result = response.json()
                metadata = result['data']['metadata']
                print(f"\n📊 Parsed Results:")
                print(f"   Rules: {metadata.get('rules_parsed', 0)}")
                print(f"   Address Objects: {metadata.get('address_object_count', 0)}")
                print(f"   Service Objects: {metadata.get('service_object_count', 0)}")
                return response.json()
            else:
                print(f"\n❌ Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

if __name__ == "__main__":
    test_set_format_upload()
