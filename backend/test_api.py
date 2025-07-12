import requests
import json

def test_file_upload():
    """Test the file upload endpoint with our sample XML config."""
    url = "http://127.0.0.1:8000/api/v1/audits"
    
    # Prepare the file and form data
    with open("test_config.xml", "rb") as f:
        files = {"file": ("test_config.xml", f, "application/xml")}
        data = {"session_name": "Test Session"}
        
        try:
            response = requests.post(url, files=files, data=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("\n✅ File upload and parsing successful!")
                return response.json()
            else:
                print(f"\n❌ Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

if __name__ == "__main__":
    test_file_upload()
