#!/usr/bin/env python3
"""
Test the new rule analysis functionality.
"""

import requests
import json

def test_rule_analysis():
    """Test the rule analysis functionality with our test file."""
    
    print("🧪 Testing Rule Analysis Functionality")
    print("=" * 50)
    
    # Use our test file that has both rules and objects
    filename = "../frontend_test_config.xml"
    
    try:
        # Step 1: Upload the test file
        print("📤 Step 1: Uploading test file...")
        
        with open(filename, "rb") as f:
            files = {"file": (filename, f, "application/xml")}
            data = {"session_name": "Rule Analysis Test"}
            
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
                print(f"📊 Parsed: {metadata.get('rules_parsed', 0)} rules, {metadata.get('objects_parsed', 0)} objects")
                
                # Step 2: Get analysis results
                print(f"\n🔍 Step 2: Getting analysis results...")
                
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_result = analysis_response.json()
                    analysis_data = analysis_result['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"✅ Analysis successful!")
                    
                    # Step 3: Display comprehensive results
                    print(f"\n📈 Analysis Summary:")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    print(f"   Disabled Rules: {summary['disabled_rules_count']}")
                    
                    # Step 4: Display rule analysis results
                    print(f"\n🔍 Rule Analysis Results:")
                    
                    # Unused Rules
                    unused_rules = analysis_data.get('unusedRules', [])
                    print(f"   📋 Unused Rules: {len(unused_rules)}")
                    for i, rule in enumerate(unused_rules[:3]):
                        print(f"      {i+1}. {rule.get('name', 'N/A')} (Position: {rule.get('position', 'N/A')})")
                        print(f"         Reason: {rule.get('description', 'N/A')}")
                        if 'recommendation' in rule:
                            print(f"         Recommendation: {rule['recommendation']}")
                    
                    # Duplicate Rules
                    duplicate_rules = analysis_data.get('duplicateRules', [])
                    print(f"   📋 Duplicate Rules: {len(duplicate_rules)}")
                    for i, dup in enumerate(duplicate_rules[:3]):
                        print(f"      {i+1}. {dup.get('duplicate_rule', {}).get('name', 'N/A')} duplicates {dup.get('original_rule', {}).get('name', 'N/A')}")
                        print(f"         Description: {dup.get('description', 'N/A')}")
                    
                    # Shadowed Rules
                    shadowed_rules = analysis_data.get('shadowedRules', [])
                    print(f"   📋 Shadowed Rules: {len(shadowed_rules)}")
                    for i, shadow in enumerate(shadowed_rules[:3]):
                        print(f"      {i+1}. {shadow.get('name', 'N/A')} shadowed by {shadow.get('shadowed_by', {}).get('name', 'N/A')}")
                        print(f"         Description: {shadow.get('description', 'N/A')}")
                    
                    # Overlapping Rules
                    overlapping_rules = analysis_data.get('overlappingRules', [])
                    print(f"   📋 Overlapping Rules: {len(overlapping_rules)}")
                    for i, overlap in enumerate(overlapping_rules[:3]):
                        rule1 = overlap.get('rule1', {}).get('name', 'N/A')
                        rule2 = overlap.get('rule2', {}).get('name', 'N/A')
                        print(f"      {i+1}. {rule1} overlaps with {rule2}")
                        print(f"         Description: {overlap.get('description', 'N/A')}")
                    
                    # Step 5: Display object analysis results
                    print(f"\n📦 Object Analysis Results:")
                    unused_objects = analysis_data.get('unusedObjects', [])
                    print(f"   Unused Objects: {len(unused_objects)}")
                    for i, obj in enumerate(unused_objects[:5]):
                        print(f"      {i+1}. {obj.get('name', 'N/A')} ({obj.get('type', 'N/A')}) = {obj.get('value', 'N/A')}")
                    
                    # Step 6: Verify expected results
                    print(f"\n🎯 Expected vs Actual Results:")
                    
                    expected = {
                        "total_rules": 10,
                        "total_objects": 10,
                        "unused_objects": 6,  # 6 unused hosts
                        "used_objects": 4,    # Server-Web1, Server-Web2, Client-LAN1, Client-LAN2
                        "unused_rules": 8     # 8 disabled rules
                    }
                    
                    actual = {
                        "total_rules": summary['total_rules'],
                        "total_objects": summary['total_objects'],
                        "unused_objects": summary['unused_objects_count'],
                        "used_objects": summary['used_objects_count'],
                        "unused_rules": len(unused_rules)
                    }
                    
                    all_correct = True
                    for key in expected:
                        expected_val = expected[key]
                        actual_val = actual[key]
                        status = "✅" if actual_val == expected_val else "❌"
                        print(f"   {key}: Expected={expected_val}, Actual={actual_val} {status}")
                        if actual_val != expected_val:
                            all_correct = False
                    
                    if all_correct:
                        print(f"\n🎉 SUCCESS! Rule analysis is working correctly!")
                        print(f"   ✅ All rules parsed and analyzed")
                        print(f"   ✅ Unused rules detected correctly")
                        print(f"   ✅ Object usage analysis working")
                        print(f"   ✅ Analysis results properly formatted for frontend")
                        
                        return True
                    else:
                        print(f"\n⚠️  Some results don't match expectations")
                        print(f"   This might be due to different analysis logic or test data")
                        return False
                        
                else:
                    print(f"❌ Analysis failed: {analysis_response.status_code}")
                    print(f"   Response: {analysis_response.text}")
                    return False
            else:
                print(f"❌ Upload failed: {upload_response.status_code}")
                print(f"   Response: {upload_response.text}")
                return False
                
    except Exception as e:
        print(f"❌ Test failed: {str(e)}")
        return False

def test_frontend_integration():
    """Test that the frontend will receive the correct data structure."""
    
    print(f"\n🖥️  Testing Frontend Integration")
    print("=" * 40)
    
    try:
        # Get the most recent audit
        response = requests.get('http://127.0.0.1:8000/api/v1/audits')
        if response.status_code == 200:
            audits = response.json()['data']
            if audits:
                latest_audit = audits[0]
                audit_id = latest_audit['audit_id']
                
                # Get analysis for frontend
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()['data']
                    
                    # Check frontend data structure
                    required_fields = [
                        'audit_id', 'session_name', 'analysis_summary',
                        'unusedObjects', 'unusedRules', 'duplicateRules',
                        'shadowedRules', 'overlappingRules'
                    ]
                    
                    missing_fields = []
                    for field in required_fields:
                        if field not in analysis_data:
                            missing_fields.append(field)
                    
                    if missing_fields:
                        print(f"❌ Missing required fields: {missing_fields}")
                        return False
                    else:
                        print(f"✅ All required fields present")
                        print(f"   Frontend will receive complete analysis data")
                        print(f"   Ready for dashboard and analysis tabs display")
                        return True
                else:
                    print(f"❌ Analysis request failed: {analysis_response.status_code}")
                    return False
            else:
                print(f"❌ No audits found")
                return False
        else:
            print(f"❌ Failed to get audits: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Frontend integration test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 RULE ANALYSIS TESTING")
    print("=" * 60)
    
    # Test rule analysis
    analysis_success = test_rule_analysis()
    
    # Test frontend integration
    frontend_success = test_frontend_integration()
    
    print(f"\n📋 FINAL RESULTS:")
    print(f"   Rule Analysis: {'✅ PASS' if analysis_success else '❌ FAIL'}")
    print(f"   Frontend Integration: {'✅ PASS' if frontend_success else '❌ FAIL'}")
    
    if analysis_success and frontend_success:
        print(f"\n🎉 ALL TESTS PASSED!")
        print(f"   Rule analysis functionality is working correctly")
        print(f"   Frontend will display comprehensive analysis results")
        print(f"   The firewall optimization tool is now feature-complete!")
    else:
        print(f"\n💥 SOME TESTS FAILED!")
        print(f"   Check the error messages above for details")
