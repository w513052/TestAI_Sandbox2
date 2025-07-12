#!/usr/bin/env python3
"""
Test the fixed object name parsing to ensure clean object names are stored.
"""

import requests

def test_fixed_object_names():
    """Test that object names are now stored correctly."""
    
    print("🧪 Testing Fixed Object Name Parsing")
    print("=" * 50)
    
    try:
        # Upload the test file again with the fixed parser
        with open("../test_expected_format.txt", "rb") as f:
            files = {"file": ("test_expected_format_fixed.txt", f, "text/plain")}
            data = {"session_name": "Test Fixed Object Names"}
            
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
                
                # Get analysis results
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"\n📈 Analysis Results (Fixed):")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    print(f"   Redundant Objects: {summary.get('redundant_objects_count', 0)}")
                    
                    # Show object categorization
                    unused_objects = analysis_data.get('unusedObjects', [])
                    redundant_objects = analysis_data.get('redundantObjects', [])
                    
                    print(f"\n📦 Object Analysis (Fixed):")
                    print(f"   Unused Objects ({len(unused_objects)}):")
                    for obj in unused_objects:
                        print(f"      - {obj['name']} = {obj['value']}")
                    
                    print(f"   Redundant Objects ({len(redundant_objects)}):")
                    for obj in redundant_objects:
                        print(f"      - {obj['name']} = {obj['value']}")
                    
                    # Calculate usage rate
                    total_objects = summary['total_objects']
                    used_objects = summary['used_objects_count']
                    usage_rate = (used_objects / total_objects * 100) if total_objects > 0 else 0
                    
                    print(f"\n🎯 Object Usage Analysis (Fixed):")
                    print(f"   Total Objects: {total_objects}")
                    print(f"   Used Objects: {used_objects}")
                    print(f"   Usage Rate: {usage_rate:.1f}%")
                    
                    # Check against your expected breakdown
                    expected = {
                        "total_objects": 17,
                        "total_rules": 17,
                        "unused_objects": 2,  # Backup-Server-01, Monitoring-Host-01
                        "redundant_objects": 5  # 5 redundant objects
                    }
                    
                    actual = {
                        "total_objects": summary['total_objects'],
                        "total_rules": summary['total_rules'],
                        "unused_objects": summary['unused_objects_count'],
                        "redundant_objects": summary.get('redundant_objects_count', 0)
                    }
                    
                    print(f"\n🎯 Your Expected Breakdown vs Actual (Fixed):")
                    print(f"   Expected: Total Address Objects: 17 (12 original + 5 redundant)")
                    print(f"   Expected: Unused Address Objects: 2 (Backup-Server-01, Monitoring-Host-01)")
                    print(f"   Expected: Total Security Policies: 17 (10 original + 5 redundant + 2 duplicate)")
                    
                    print(f"\n   Actual Results:")
                    all_correct = True
                    for key in expected:
                        expected_val = expected[key]
                        actual_val = actual[key]
                        status = "✅" if actual_val == expected_val else "❌"
                        print(f"      {key}: Expected={expected_val}, Actual={actual_val} {status}")
                        if actual_val != expected_val:
                            all_correct = False
                    
                    # Check specific unused objects
                    expected_unused = {"Backup-Server-01", "Monitoring-Host-01"}
                    actual_unused = {obj['name'] for obj in unused_objects}
                    
                    print(f"\n🔍 Specific Unused Objects Check:")
                    print(f"   Expected unused: {expected_unused}")
                    print(f"   Actual unused: {actual_unused}")
                    
                    if expected_unused.issubset(actual_unused):
                        print(f"   ✅ Expected unused objects found!")
                    else:
                        missing = expected_unused - actual_unused
                        print(f"   ❌ Missing expected unused objects: {missing}")
                        all_correct = False
                    
                    # Show which objects are now being used
                    if used_objects > 0:
                        print(f"\n🎉 SUCCESS! Object usage analysis is now working!")
                        print(f"   ✅ Object names are stored correctly")
                        print(f"   ✅ Rule references match object names")
                        print(f"   ✅ Usage rate: {usage_rate:.1f}%")
                        
                        # Show rule analysis
                        print(f"\n📋 Rule Analysis:")
                        print(f"   Unused Rules: {len(analysis_data.get('unusedRules', []))}")
                        print(f"   Duplicate Rules: {len(analysis_data.get('duplicateRules', []))}")
                        print(f"   Shadowed Rules: {len(analysis_data.get('shadowedRules', []))}")
                        print(f"   Overlapping Rules: {len(analysis_data.get('overlappingRules', []))}")
                        
                        return all_correct
                    else:
                        print(f"\n❌ Object usage analysis still not working")
                        print(f"   All objects still marked as unused")
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
    print("🚀 TESTING FIXED OBJECT NAME PARSING")
    print("=" * 60)
    
    success = test_fixed_object_names()
    
    if success:
        print(f"\n🎉 OBJECT NAME PARSING FIX SUCCESSFUL!")
        print(f"   Object names are now stored correctly")
        print(f"   Object usage analysis is working")
        print(f"   Results match your expected breakdown")
        print(f"   Set format parsing is fully functional")
    else:
        print(f"\n💥 OBJECT NAME PARSING STILL HAS ISSUES!")
        print(f"   Need further investigation")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. If successful, test with your original complex file")
    print(f"   2. Verify the breakdown matches your expectations")
    print(f"   3. Check frontend display for correct categorization")
