import requests
import json

def test_usage_analysis():
    """Test the object usage analysis with a config that has object references."""
    url = "http://127.0.0.1:8000/api/v1/audits/"
    
    # Prepare the file and form data
    with open("test_usage_config.xml", "rb") as f:
        files = {"file": ("test_usage_config.xml", f, "application/xml")}
        data = {"session_name": "Object Usage Test Session"}
        
        try:
            response = requests.post(url, files=files, data=data)
            print(f"Status Code: {response.status_code}")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
            
            if response.status_code == 200:
                print("\n✅ Object usage analysis test successful!")
                result = response.json()
                metadata = result['data']['metadata']
                print(f"\n📊 Parsed Results:")
                print(f"   Rules: {metadata.get('rules_parsed', 0)}")
                print(f"   Address Objects: {metadata.get('address_object_count', 0)}")
                print(f"   Service Objects: {metadata.get('service_object_count', 0)}")
                print(f"\n🎯 This config should show object usage analysis in the logs!")
                return response.json()
            else:
                print(f"\n❌ Error: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

if __name__ == "__main__":
    test_usage_analysis()
