import requests
import json

def test_20_unused_objects():
    """Test with a file that has 20 objects and 0 rules (all should be unused)."""
    
    # First, check what files we have available
    import os
    files = [f for f in os.listdir('.') if f.endswith('.xml')]
    print(f"Available XML files: {files}")
    
    # Use the test file with 20 objects and 0 rules
    test_file = "test_20_objects.xml"

    if not os.path.exists(test_file):
        print(f"❌ Test file {test_file} not found")
        return

    print(f"Using test file: {test_file}")
    
    # Upload the file
    upload_url = "http://127.0.0.1:8000/api/v1/audits/"
    
    with open(test_file, "rb") as f:
        files_data = {"file": (test_file, f, "application/xml")}
        data = {"session_name": "Test 20 Unused Objects"}
        
        try:
            upload_response = requests.post(upload_url, files=files_data, data=data)
            print(f"Upload Status: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                upload_result = upload_response.json()
                audit_id = upload_result['data']['audit_id']
                print(f"✅ File uploaded successfully! Audit ID: {audit_id}")
                
                # Get analysis results
                analysis_url = f"http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis"
                analysis_response = requests.get(analysis_url)
                
                print(f"\nAnalysis Status: {analysis_response.status_code}")
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    data = analysis_result['data']
                    
                    print(f"\n📊 Analysis Summary:")
                    print(f"   Total Rules: {data['analysis_summary']['total_rules']}")
                    print(f"   Total Objects: {data['analysis_summary']['total_objects']}")
                    print(f"   Unused Objects: {data['analysis_summary']['unused_objects_count']}")
                    print(f"   Used Objects: {data['analysis_summary']['used_objects_count']}")
                    
                    if data['analysis_summary']['unused_objects_count'] > 0:
                        print(f"\n🎯 SUCCESS! Found {data['analysis_summary']['unused_objects_count']} unused objects!")
                        print(f"First few unused objects:")
                        for i, obj in enumerate(data['unusedObjects'][:5]):
                            print(f"   {i+1}. {obj['name']} ({obj['type']})")
                        if len(data['unusedObjects']) > 5:
                            print(f"   ... and {len(data['unusedObjects']) - 5} more")
                    else:
                        print("❌ No unused objects found")
                    
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
    test_20_unused_objects()
