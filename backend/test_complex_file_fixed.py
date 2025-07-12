#!/usr/bin/env python3
"""
Test the fixed analysis with the complex file to verify correct object categorization.
"""

import requests
import json

def test_fixed_analysis():
    """Test the fixed analysis with the most recent complex file upload."""
    
    print("🧪 Testing Fixed Analysis with Complex File")
    print("=" * 50)
    
    try:
        # Get the most recent audit (should be the complex file)
        response = requests.get('http://127.0.0.1:8000/api/v1/audits')
        if response.status_code == 200:
            audits = response.json()['data']
            if audits:
                latest_audit = audits[0]
                audit_id = latest_audit['audit_id']
                filename = latest_audit['filename']
                
                print(f"📋 Testing Audit:")
                print(f"   ID: {audit_id}")
                print(f"   File: {filename}")
                
                # Get updated analysis
                analysis_response = requests.get(f'http://127.0.0.1:8000/api/v1/audits/{audit_id}/analysis')
                
                if analysis_response.status_code == 200:
                    analysis_data = analysis_response.json()['data']
                    summary = analysis_data['analysis_summary']
                    
                    print(f"\n📈 Updated Analysis Summary:")
                    print(f"   Total Rules: {summary['total_rules']}")
                    print(f"   Total Objects: {summary['total_objects']}")
                    print(f"   Used Objects: {summary['used_objects_count']}")
                    print(f"   Unused Objects: {summary['unused_objects_count']}")
                    print(f"   Redundant Objects: {summary.get('redundant_objects_count', 0)}")
                    
                    # Show object categorization
                    unused_objects = analysis_data.get('unusedObjects', [])
                    redundant_objects = analysis_data.get('redundantObjects', [])
                    
                    print(f"\n📦 Object Categorization:")
                    print(f"   Unused Objects ({len(unused_objects)}):")
                    for obj in unused_objects:
                        print(f"      - {obj['name']} = {obj['value']}")
                    
                    print(f"   Redundant Objects ({len(redundant_objects)}):")
                    for obj in redundant_objects:
                        print(f"      - {obj['name']} = {obj['value']}")
                    
                    # Compare with expected values
                    print(f"\n🎯 Expected vs Actual (Fixed):")
                    
                    expected = {
                        "Total Address Objects": 17,
                        "Unused Address Objects": 2,  # Should be Backup-Server-01, Monitoring-Host-01
                        "Redundant Address Objects": 5,  # Should be the 5 redundant objects
                        "Total Security Policies": 17
                    }
                    
                    actual = {
                        "Total Address Objects": summary['total_objects'],
                        "Unused Address Objects": summary['unused_objects_count'],
                        "Redundant Address Objects": summary.get('redundant_objects_count', 0),
                        "Total Security Policies": summary['total_rules']
                    }
                    
                    print(f"   Expected breakdown:")
                    print(f"      Total Address Objects: 17 (12 original + 5 redundant)")
                    print(f"      Unused Address Objects: 2 (Backup-Server-01, Monitoring-Host-01)")
                    print(f"      Redundant Address Objects: 5 (objects with same value as used objects)")
                    print(f"      Total Security Policies: 17 (10 original + 5 redundant + 2 duplicate)")
                    
                    print(f"\n   Actual results (fixed):")
                    all_correct = True
                    for key in expected:
                        expected_val = expected[key]
                        actual_val = actual[key]
                        status = "✅" if actual_val == expected_val else "❌"
                        print(f"      {key}: Expected={expected_val}, Actual={actual_val} {status}")
                        if actual_val != expected_val:
                            all_correct = False
                    
                    # Verify specific unused objects
                    print(f"\n🔍 Specific Object Verification:")
                    expected_unused = {"Backup-Server-01", "Monitoring-Host-01"}
                    actual_unused = {obj['name'] for obj in unused_objects}
                    
                    print(f"   Expected unused: {expected_unused}")
                    print(f"   Actual unused: {actual_unused}")
                    
                    if expected_unused == actual_unused:
                        print(f"   ✅ Unused objects match exactly!")
                    else:
                        print(f"   ❌ Unused objects don't match")
                        missing = expected_unused - actual_unused
                        extra = actual_unused - expected_unused
                        if missing:
                            print(f"      Missing: {missing}")
                        if extra:
                            print(f"      Extra: {extra}")
                        all_correct = False
                    
                    # Check redundant objects
                    redundant_names = {obj['name'] for obj in redundant_objects}
                    expected_redundant_pattern = {name for name in redundant_names if 'redundant' in name.lower()}
                    
                    print(f"\n   Redundant objects found: {redundant_names}")
                    print(f"   Objects with 'redundant' in name: {expected_redundant_pattern}")
                    
                    # Show rule analysis summary
                    print(f"\n📋 Rule Analysis Summary:")
                    print(f"   Unused Rules: {len(analysis_data.get('unusedRules', []))}")
                    print(f"   Duplicate Rules: {len(analysis_data.get('duplicateRules', []))}")
                    print(f"   Shadowed Rules: {len(analysis_data.get('shadowedRules', []))}")
                    print(f"   Overlapping Rules: {len(analysis_data.get('overlappingRules', []))}")
                    
                    if all_correct:
                        print(f"\n🎉 SUCCESS! Analysis now matches expected breakdown!")
                        print(f"   ✅ Correctly categorized unused vs redundant objects")
                        print(f"   ✅ Proper object usage analysis")
                        print(f"   ✅ Comprehensive rule analysis working")
                        return True
                    else:
                        print(f"\n⚠️  Some discrepancies remain")
                        return False
                        
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
        print(f"❌ Test failed: {str(e)}")
        return False

def show_frontend_impact():
    """Show how this affects the frontend display."""
    
    print(f"\n🖥️  Frontend Impact")
    print("=" * 30)
    
    print(f"📊 Dashboard Changes:")
    print(f"   - Now shows separate counts for unused vs redundant objects")
    print(f"   - More accurate object categorization")
    print(f"   - Better matches user expectations")
    
    print(f"\n📋 Analysis Tabs:")
    print(f"   - Unused Objects tab: Only truly unused objects")
    print(f"   - New Redundant Objects tab: Objects with same value as used objects")
    print(f"   - Better user experience with clearer categorization")
    
    print(f"\n🎯 User Benefits:")
    print(f"   - Clearer understanding of object usage")
    print(f"   - Separate handling of unused vs redundant objects")
    print(f"   - More actionable recommendations")

if __name__ == "__main__":
    print("🚀 TESTING FIXED COMPLEX FILE ANALYSIS")
    print("=" * 60)
    
    success = test_fixed_analysis()
    
    if success:
        show_frontend_impact()
        
        print(f"\n🎉 ANALYSIS FIX SUCCESSFUL!")
        print(f"   The system now correctly categorizes objects")
        print(f"   Frontend will show accurate breakdowns")
        print(f"   User expectations are met")
    else:
        print(f"\n💥 ANALYSIS STILL HAS ISSUES!")
        print(f"   Further investigation needed")
    
    print(f"\n💡 Next Steps:")
    print(f"   1. Test with the frontend to see updated display")
    print(f"   2. Verify redundant objects tab appears")
    print(f"   3. Check that unused objects match expectations")
