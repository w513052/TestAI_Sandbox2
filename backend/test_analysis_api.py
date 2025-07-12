import requests
import json

def test_analysis_endpoint():
    """Test the new analysis endpoint to see unused objects."""
    
    # First, upload a file to get an audit_id
    upload_url = "http://127.0.0.1:8000/api/v1/audits/"
    
    with open("test_usage_config.xml", "rb") as f:
        files = {"file": ("test_usage_config.xml", f, "application/xml")}
        data = {"session_name": "Analysis Test Session"}
        
        try:
            upload_response = requests.post(upload_url, files=files, data=data)
            print(f"Upload Status: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                upload_result = upload_response.json()
                audit_id = upload_result['data']['audit_id']
                print(f"✅ File uploaded successfully! Audit ID: {audit_id}")
                
                # Now test the analysis endpoint
                analysis_url = f"http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis"
                analysis_response = requests.get(analysis_url)
                
                print(f"\nAnalysis Status: {analysis_response.status_code}")
                print(f"Analysis Response: {json.dumps(analysis_response.json(), indent=2)}")
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    data = analysis_result['data']
                    
                    print(f"\n📊 Analysis Summary:")
                    print(f"   Total Rules: {data['analysis_summary']['total_rules']}")
                    print(f"   Total Objects: {data['analysis_summary']['total_objects']}")
                    print(f"   Unused Objects: {data['analysis_summary']['unused_objects_count']}")
                    print(f"   Used Objects: {data['analysis_summary']['used_objects_count']}")
                    
                    print(f"\n🔍 Unused Objects Details:")
                    for obj in data['unusedObjects']:
                        print(f"   - {obj['name']} ({obj['type']}): {obj['description']}")
                    
                    return analysis_result
                else:
                    print(f"❌ Analysis failed: {analysis_response.status_code}")
                    return None
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Request failed: {str(e)}")
            return None

if __name__ == "__main__":
    test_analysis_endpoint()
