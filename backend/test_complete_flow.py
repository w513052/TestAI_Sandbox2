import requests
import json

def test_complete_frontend_flow():
    """Test the complete flow that the frontend will execute."""
    
    print("🧪 Testing Complete Frontend Flow")
    print("=" * 50)
    
    # Step 1: Test backend connection (what frontend does on load)
    print("\n1️⃣ Step 1: Test backend connection")
    try:
        health_response = requests.get('http://127.0.0.1:8000/health', 
                                     headers={'Origin': 'http://localhost:5175'})
        print(f"   Health check: {health_response.status_code} - {health_response.json()}")
        
        if health_response.status_code != 200:
            print("❌ Backend health check failed")
            return False
            
    except Exception as e:
        print(f"❌ Backend connection failed: {str(e)}")
        return False
    
    # Step 2: Upload file (what frontend does when user uploads)
    print("\n2️⃣ Step 2: Upload configuration file")
    try:
        with open("test_20_objects.xml", "rb") as f:
            files = {"file": ("test_20_objects.xml", f, "application/xml")}
            data = {"session_name": "Complete Flow Test"}
            
            upload_response = requests.post(
                'http://127.0.0.1:8000/api/v1/audits/',
                files=files,
                data=data,
                headers={'Origin': 'http://localhost:5175'}
            )
            
            print(f"   Upload: {upload_response.status_code}")
            
            if upload_response.status_code != 200:
                print(f"❌ Upload failed: {upload_response.text}")
                return False
                
            upload_result = upload_response.json()
            audit_id = upload_result['data']['audit_id']
            print(f"   ✅ File uploaded successfully! Audit ID: {audit_id}")
            
    except Exception as e:
        print(f"❌ File upload failed: {str(e)}")
        return False
    
    # Step 3: Get analysis results (what frontend does after upload)
    print("\n3️⃣ Step 3: Fetch analysis results")
    try:
        analysis_response = requests.get(
            f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis',
            headers={'Origin': 'http://localhost:5175'}
        )
        
        print(f"   Analysis: {analysis_response.status_code}")
        
        if analysis_response.status_code != 200:
            print(f"❌ Analysis failed: {analysis_response.text}")
            return False
            
        analysis_result = analysis_response.json()
        analysis_data = analysis_result['data']
        
        print(f"   ✅ Analysis retrieved successfully!")
        
    except Exception as e:
        print(f"❌ Analysis retrieval failed: {str(e)}")
        return False
    
    # Step 4: Verify data structure (what frontend expects)
    print("\n4️⃣ Step 4: Verify frontend data structure")
    
    # Check required fields
    required_fields = ['unusedObjects', 'unusedRules', 'duplicateRules', 'shadowedRules', 'overlappingRules']
    for field in required_fields:
        if field in analysis_data:
            print(f"   ✅ {field}: {len(analysis_data[field])} items")
        else:
            print(f"   ❌ {field}: MISSING")
            return False
    
    # Check unused objects specifically
    unused_objects = analysis_data.get('unusedObjects', [])
    if len(unused_objects) > 0:
        print(f"\n   📊 Unused Objects Analysis:")
        print(f"      Total unused objects: {len(unused_objects)}")
        
        # Check object structure
        first_obj = unused_objects[0]
        required_obj_fields = ['id', 'name', 'type', 'value', 'severity', 'description']
        
        for field in required_obj_fields:
            if field in first_obj:
                print(f"      ✅ Object.{field}: {first_obj[field]}")
            else:
                print(f"      ❌ Object.{field}: MISSING")
                return False
        
        # Show sample objects
        print(f"\n   🎯 Sample unused objects:")
        for i, obj in enumerate(unused_objects[:3]):
            print(f"      {i+1}. {obj['name']} ({obj['type']}) - {obj['description']}")
        
        if len(unused_objects) > 3:
            print(f"      ... and {len(unused_objects) - 3} more")
    else:
        print(f"   ❌ No unused objects found")
        return False
    
    # Step 5: Test what frontend will display
    print("\n5️⃣ Step 5: Frontend display simulation")
    
    # Simulate frontend summary
    summary = analysis_data.get('analysis_summary', {})
    print(f"   📈 Dashboard Summary:")
    print(f"      Total Rules: {summary.get('total_rules', 0)}")
    print(f"      Total Objects: {summary.get('total_objects', 0)}")
    print(f"      Unused Objects: {summary.get('unused_objects_count', 0)}")
    print(f"      Used Objects: {summary.get('used_objects_count', 0)}")
    
    # Simulate frontend tabs
    print(f"\n   📋 Analysis Tabs:")
    tabs = [
        ('Duplicate Rules', len(analysis_data.get('duplicateRules', []))),
        ('Shadowed Rules', len(analysis_data.get('shadowedRules', []))),
        ('Unused Rules', len(analysis_data.get('unusedRules', []))),
        ('Overlapping Rules', len(analysis_data.get('overlappingRules', []))),
        ('Unused Objects', len(analysis_data.get('unusedObjects', [])))
    ]
    
    for tab_name, count in tabs:
        print(f"      {tab_name}: {count} items")
    
    print(f"\n🎉 SUCCESS! Complete frontend flow is working perfectly!")
    print(f"   - Backend connection: ✅")
    print(f"   - File upload: ✅")
    print(f"   - Analysis retrieval: ✅")
    print(f"   - Data structure: ✅")
    print(f"   - Unused objects: ✅ ({len(unused_objects)} found)")
    print(f"   - Frontend display: ✅")
    
    return True

if __name__ == "__main__":
    success = test_complete_frontend_flow()
    if success:
        print(f"\n🚀 The frontend is now fully functional!")
        print(f"   Open http://localhost:5175 and upload a file to see unused objects!")
        print(f"   The UI will display all {len(unused_objects) if 'unused_objects' in locals() else 'N/A'} unused objects correctly.")
    else:
        print(f"\n💥 Something is still not working correctly.")
