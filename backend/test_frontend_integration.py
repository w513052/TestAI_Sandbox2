import requests
import json

def test_frontend_integration():
    """Test the complete frontend integration flow."""
    
    print("🧪 Testing Frontend Integration Flow")
    print("=" * 50)
    
    # Step 1: Upload file (simulating frontend upload)
    print("\n1️⃣ Step 1: Upload file")
    upload_url = "http://127.0.0.1:8000/api/v1/audits/"
    
    with open("test_20_objects.xml", "rb") as f:
        files = {"file": ("test_20_objects.xml", f, "application/xml")}
        data = {"session_name": "Frontend Integration Test"}
        
        try:
            upload_response = requests.post(upload_url, files=files, data=data)
            print(f"   Upload Status: {upload_response.status_code}")
            
            if upload_response.status_code == 200:
                upload_result = upload_response.json()
                audit_id = upload_result['data']['audit_id']
                print(f"   ✅ File uploaded successfully! Audit ID: {audit_id}")
                
                # Step 2: Get analysis results (simulating frontend analysis call)
                print("\n2️⃣ Step 2: Fetch analysis results")
                analysis_url = f"http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis"
                analysis_response = requests.get(analysis_url)
                
                print(f"   Analysis Status: {analysis_response.status_code}")
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    analysis_data = analysis_result['data']
                    
                    print(f"   ✅ Analysis results retrieved successfully!")
                    
                    # Step 3: Verify data structure matches frontend expectations
                    print("\n3️⃣ Step 3: Verify data structure")
                    
                    required_fields = ['unusedObjects', 'unusedRules', 'duplicateRules', 'shadowedRules', 'overlappingRules']
                    for field in required_fields:
                        if field in analysis_data:
                            print(f"   ✅ {field}: {len(analysis_data[field])} items")
                        else:
                            print(f"   ❌ {field}: MISSING")
                    
                    # Step 4: Test unused objects data
                    print("\n4️⃣ Step 4: Verify unused objects data")
                    unused_objects = analysis_data.get('unusedObjects', [])
                    
                    if len(unused_objects) > 0:
                        print(f"   ✅ Found {len(unused_objects)} unused objects")
                        
                        # Check first unused object structure
                        first_obj = unused_objects[0]
                        required_obj_fields = ['id', 'name', 'type', 'value', 'severity', 'description']
                        
                        print("   📋 First unused object structure:")
                        for field in required_obj_fields:
                            if field in first_obj:
                                print(f"      ✅ {field}: {first_obj[field]}")
                            else:
                                print(f"      ❌ {field}: MISSING")
                        
                        # Show sample unused objects
                        print(f"\n   📊 Sample unused objects:")
                        for i, obj in enumerate(unused_objects[:3]):
                            print(f"      {i+1}. {obj['name']} ({obj['type']}) - {obj['description']}")
                        
                        if len(unused_objects) > 3:
                            print(f"      ... and {len(unused_objects) - 3} more")
                        
                        print(f"\n🎉 SUCCESS! Frontend integration is working correctly!")
                        print(f"   - File upload: ✅")
                        print(f"   - Analysis retrieval: ✅") 
                        print(f"   - Data structure: ✅")
                        print(f"   - Unused objects: ✅ ({len(unused_objects)} found)")
                        
                        return True
                    else:
                        print("   ❌ No unused objects found")
                        return False
                else:
                    print(f"   ❌ Analysis failed: {analysis_response.status_code}")
                    print(f"   Response: {analysis_response.text}")
                    return False
            else:
                print(f"   ❌ Upload failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Test failed: {str(e)}")
            return False

if __name__ == "__main__":
    success = test_frontend_integration()
    if success:
        print(f"\n🚀 The frontend should now display unused objects correctly!")
        print(f"   Open http://localhost:5175 and upload a file to see the results.")
    else:
        print(f"\n💥 Integration test failed - check the issues above.")
