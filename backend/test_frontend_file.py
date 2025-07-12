#!/usr/bin/env python3
"""
Test the frontend test file to make sure it produces the expected results.
"""

import requests
import json

def test_frontend_file():
    """Test the frontend test file."""
    
    print("🧪 Testing Frontend Test File")
    print("=" * 40)
    
    filename = "../frontend_test_config.xml"
    
    try:
        with open(filename, "rb") as f:
            files = {"file": ("frontend_test_config.xml", f, "application/xml")}
            data = {"session_name": "Frontend Test File"}
            
            upload_response = requests.post(
                'http://127.0.0.1:8000/api/v1/audits/',
                files=files,
                data=data
            )
            
            if upload_response.status_code == 200:
                result = upload_response.json()
                audit_id = result['data']['audit_id']
                metadata = result['data']['metadata']
                
                print(f"✅ Upload successful! Audit ID: {audit_id}")
                print(f"📊 Parsing Results:")
                print(f"   Rules parsed: {metadata.get('rules_parsed', 0)}")
                print(f"   Objects parsed: {metadata.get('objects_parsed', 0)}")
                
                # Get analysis
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    analysis_data = analysis_result['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"\n📈 Analysis Results:")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    print(f"   Disabled Rules: {summary['disabled_rules_count']}")
                    
                    unused_objects = analysis_data.get('unusedObjects', [])
                    unused_rules = analysis_data.get('unusedRules', [])
                    
                    print(f"\n📦 Unused Objects: {len(unused_objects)}")
                    for obj in unused_objects:
                        print(f"   - {obj['name']} ({obj['type']})")
                    
                    print(f"\n📋 Unused Rules: {len(unused_rules)}")
                    for rule in unused_rules:
                        print(f"   - {rule['name']} ({rule.get('reason', 'N/A')})")
                    
                    print(f"\n🎯 Expected Frontend Display:")
                    print(f"   Dashboard:")
                    print(f"      Total Rules: {summary['total_rules']}")
                    print(f"      Total Objects: {summary['total_objects']}")
                    print(f"      Unused Objects: {summary['unused_objects_count']}")
                    print(f"      Used Objects: {summary['used_objects_count']}")
                    
                    print(f"   Analysis Tabs:")
                    print(f"      Unused Objects: {len(unused_objects)} items")
                    print(f"      Unused Rules: {len(unused_rules)} items")
                    
                    return True
                else:
                    print(f"❌ Analysis failed: {analysis_response.status_code}")
                    return False
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_frontend_file()
    
    if success:
        print(f"\n✅ Frontend test file is ready!")
        print(f"   Upload this file in the browser to test frontend integration")
        print(f"   Check browser console for debug logs")
    else:
        print(f"\n❌ Frontend test file has issues")
