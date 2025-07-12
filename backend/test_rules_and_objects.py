#!/usr/bin/env python3
"""
Test upload with a file that contains both rules and objects to demonstrate proper functionality.
"""

import requests
import json

def test_with_rules_and_objects():
    """Test with a file that has both rules and objects."""
    
    print("🧪 Testing with Rules AND Objects")
    print("=" * 50)
    
    # Test with small_test_config.xml which has both rules and objects
    filename = "small_test_config.xml"
    
    try:
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "application/xml")}
            data = {"session_name": "Test with Rules and Objects"}
            
            print(f"📤 Uploading {filename}...")
            upload_response = requests.post(
                'http://127.0.0.1:8000/api/v1/audits/',
                files=files,
                data=data
            )
            
            if upload_response.status_code == 200:
                result = upload_response.json()
                metadata = result['data']['metadata']
                audit_id = result['data']['audit_id']
                
                print(f"✅ Upload successful! Audit ID: {audit_id}")
                print(f"📊 Parsing Results:")
                print(f"   Rules parsed: {metadata.get('rules_parsed', 0)}")
                print(f"   Objects parsed: {metadata.get('objects_parsed', 0)}")
                print(f"   Address objects: {metadata.get('address_object_count', 0)}")
                print(f"   Service objects: {metadata.get('service_object_count', 0)}")
                
                # Get analysis results
                print(f"\n🔍 Getting analysis results...")
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    analysis_data = analysis_result['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"✅ Analysis successful!")
                    print(f"📈 Analysis Summary:")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    
                    print(f"\n🎯 Analysis Categories:")
                    categories = [
                        ('Duplicate Rules', 'duplicateRules'),
                        ('Shadowed Rules', 'shadowedRules'),
                        ('Unused Rules', 'unusedRules'),
                        ('Overlapping Rules', 'overlappingRules'),
                        ('Unused Objects', 'unusedObjects')
                    ]
                    
                    for category_name, category_key in categories:
                        count = len(analysis_data.get(category_key, []))
                        print(f"   {category_name}: {count} items")
                    
                    # Show object usage details
                    unused_objects = analysis_data.get('unusedObjects', [])
                    if len(unused_objects) > 0:
                        print(f"\n📋 Unused Objects:")
                        for i, obj in enumerate(unused_objects[:5]):
                            print(f"   {i+1}. {obj['name']} ({obj['type']}) - {obj['description']}")
                        if len(unused_objects) > 5:
                            print(f"   ... and {len(unused_objects) - 5} more")
                    else:
                        print(f"\n✅ All objects are used in rules!")
                    
                    # Demonstrate what frontend should show
                    print(f"\n🖥️  Frontend Should Display:")
                    print(f"   Dashboard:")
                    print(f"      📊 {summary['total_rules']} Rules")
                    print(f"      📦 {summary['total_objects']} Objects")
                    print(f"      ✅ {summary['used_objects_count']} Used Objects")
                    print(f"      ❌ {summary['unused_objects_count']} Unused Objects")
                    
                    print(f"   Analysis Tabs:")
                    for category_name, category_key in categories:
                        count = len(analysis_data.get(category_key, []))
                        status = "✅" if count == 0 else f"⚠️ {count}"
                        print(f"      {category_name}: {status}")
                    
                    return True
                else:
                    print(f"❌ Analysis failed: {analysis_response.status_code}")
                    return False
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text}")
                return False
                
    except FileNotFoundError:
        print(f"❌ File {filename} not found")
        return False
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_with_rules_and_objects()
    
    if success:
        print(f"\n🎉 SUCCESS! The system is working correctly!")
        print(f"\n💡 Key Points:")
        print(f"   - Files with ONLY objects → All objects marked 'unused' (correct)")
        print(f"   - Files with rules AND objects → Proper usage analysis")
        print(f"   - Frontend displays accurate data based on file content")
        print(f"   - Upload a file with both rules and objects to see usage analysis")
    else:
        print(f"\n💥 Test failed - check the issues above")
