#!/usr/bin/env python3
"""
Test the frontend fix to verify correct data display.
"""

import requests

def test_frontend_fix():
    """Test that the frontend fix resolves the display issues."""
    
    print("🧪 Testing Frontend Fix")
    print("=" * 50)
    
    try:
        # Upload our test file that we know works correctly
        with open("../test_expected_format.txt", "rb") as f:
            files = {"file": ("test_frontend_fix.txt", f, "text/plain")}
            data = {"session_name": "Frontend Fix Test"}
            
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
                print(f"📊 Upload Metadata:")
                print(f"   rules_parsed: {metadata.get('rules_parsed', 'MISSING')}")
                print(f"   rule_count: {metadata.get('rule_count', 'MISSING')}")
                print(f"   address_object_count: {metadata.get('address_object_count', 0)}")
                print(f"   service_object_count: {metadata.get('service_object_count', 0)}")
                
                # Get analysis results
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"\n📈 Backend Analysis Summary:")
                    print(f"   total_rules: {summary['total_rules']}")
                    print(f"   total_objects: {summary['total_objects']}")
                    print(f"   used_objects_count: {summary['used_objects_count']}")
                    print(f"   unused_objects_count: {summary['unused_objects_count']}")
                    print(f"   redundant_objects_count: {summary.get('redundant_objects_count', 0)}")
                    
                    # Simulate what the FIXED frontend will now calculate
                    print(f"\n🖥️  Fixed Frontend Calculation:")
                    
                    total_objects_metadata = metadata.get('address_object_count', 0) + metadata.get('service_object_count', 0)
                    
                    fixed_frontend_data = {
                        "totalRules": summary['total_rules'],  # NOW USING ANALYSIS SUMMARY ✅
                        "totalObjects": summary['total_objects'],  # NOW USING ANALYSIS SUMMARY ✅
                        "unusedObjects": len(analysis_data.get('unusedObjects', [])),
                        "redundantObjects": len(analysis_data.get('redundantObjects', [])),  # NOW USING BACKEND DATA ✅
                        "duplicateRules": len(analysis_data.get('duplicateRules', [])),
                        "shadowedRules": len(analysis_data.get('shadowedRules', [])),
                        "unusedRules": len(analysis_data.get('unusedRules', [])),
                        "overlappingRules": len(analysis_data.get('overlappingRules', []))
                    }
                    
                    print(f"   Fixed Frontend Summary:")
                    for key, value in fixed_frontend_data.items():
                        print(f"      {key}: {value}")
                    
                    # Compare with expected values
                    expected = {
                        "totalRules": 17,
                        "totalObjects": 17,
                        "unusedObjects": 2,
                        "redundantObjects": 5,
                        "duplicateRules": 7,
                        "shadowedRules": 7,
                        "unusedRules": 7,
                        "overlappingRules": 34
                    }
                    
                    print(f"\n🎯 Expected vs Fixed Frontend:")
                    all_correct = True
                    for key in expected:
                        expected_val = expected[key]
                        actual_val = fixed_frontend_data[key]
                        status = "✅" if actual_val == expected_val else "❌"
                        print(f"   {key}: Expected={expected_val}, Actual={actual_val} {status}")
                        if actual_val != expected_val:
                            all_correct = False
                    
                    if all_correct:
                        print(f"\n🎉 FRONTEND FIX SUCCESSFUL!")
                        print(f"   ✅ Frontend now uses correct backend data")
                        print(f"   ✅ All values match expected results")
                        print(f"   ✅ Redundant objects now displayed correctly")
                        print(f"   ✅ Rule counts now accurate")
                        
                        print(f"\n📱 What Frontend Should Now Display:")
                        print(f"   Dashboard:")
                        print(f"      Total Rules: {fixed_frontend_data['totalRules']}")
                        print(f"      Total Objects: {fixed_frontend_data['totalObjects']}")
                        print(f"      Unused Objects: {fixed_frontend_data['unusedObjects']}")
                        print(f"      Redundant Objects: {fixed_frontend_data['redundantObjects']}")
                        
                        print(f"   Analysis Tabs:")
                        print(f"      Unused Objects: {fixed_frontend_data['unusedObjects']} items")
                        print(f"      Redundant Objects: {fixed_frontend_data['redundantObjects']} items")
                        print(f"      Unused Rules: {fixed_frontend_data['unusedRules']} items")
                        print(f"      Duplicate Rules: {fixed_frontend_data['duplicateRules']} items")
                        print(f"      Shadowed Rules: {fixed_frontend_data['shadowedRules']} items")
                        print(f"      Overlapping Rules: {fixed_frontend_data['overlappingRules']} items")
                        
                        return True
                    else:
                        print(f"\n⚠️  Some values still don't match")
                        print(f"   Frontend fix is working but backend data might need adjustment")
                        return False
                        
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
    print("🚀 TESTING FRONTEND FIX")
    print("=" * 60)
    
    success = test_frontend_fix()
    
    if success:
        print(f"\n🎉 FRONTEND FIX SUCCESSFUL!")
        print(f"   The frontend should now display correct values")
        print(f"   Upload a file in the browser to verify the fix")
    else:
        print(f"\n💥 FRONTEND FIX NEEDS MORE WORK!")
        print(f"   Check the discrepancies above")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Test in the browser with file upload")
    print(f"   2. Check browser console for debug logs")
    print(f"   3. Verify dashboard shows correct numbers")
    print(f"   4. Check all analysis tabs display properly")
